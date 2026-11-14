"""Planificación individual con serialización por trimestre y funcionario."""
import calendar
from datetime import date
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import Q, Sum
from django.views.decorators.http import require_http_methods
from . import local_api as api, domain_api as domain
from .models import Usuario, PeriodoGestion, ItemMeta
from .goal_models import AsignacionMeta

RESOURCE='asignaciones-metas'

def manager(user):
    return user.is_superuser or bool(user.rol_id and user.rol.estado and user.rol.nombre.strip().casefold() in ['administrador','delegado'])

def visible(request):
    qs=AsignacionMeta.objects.filter(delegacion=api.active_delegation(request)).select_related('funcionario','item','periodo')
    if not api.allowed(request.user,RESOURCE,'ver_equipo'):qs=qs.filter(funcionario=request.user)
    return qs

def representation(obj):
    return dict(id=obj.pk,version=obj.version,funcionario=obj.funcionario_id,funcionario_nombre=obj.funcionario.get_full_name() or obj.funcionario.username,item=obj.item_id,item_nombre=obj.snapshot.get('item_nombre',obj.item.nombre),periodo=obj.periodo_id,periodo_nombre=obj.snapshot.get('periodo_nombre',obj.periodo.nombre),cantidad_objetivo=format(obj.cantidad_objetivo,'.2f'),ponderacion=format(obj.ponderacion,'.2f'),observacion=obj.observacion,estado=obj.estado,fecha_asignacion=obj.fecha_asignacion.isoformat(),cerrado=obj.periodo.cerrado,snapshot=obj.snapshot)

def quarter(period):
    if type(period.anio) is not int or not 1900<=period.anio<=9999 or period.numero not in [1,2,3,4]:raise ValidationError('El periodo debe indicar año y número de trimestre.')
    month=period.numero*3
    if period.fecha_inicio!=date(period.anio,month-2,1) or period.fecha_fin!=date(period.anio,month,calendar.monthrange(period.anio,month)[1]):raise ValidationError('Las fechas deben corresponder al año y trimestre indicados.')

def number(value,label,max_digits):
    if isinstance(value,bool):raise ValidationError(label+' inválida.')
    try:result=Decimal(str(value))
    except (InvalidOperation,ValueError):raise ValidationError(label+' inválida.')
    if not result.is_finite() or result.as_tuple().exponent < -2 or result<0 or result>=Decimal(10)**max_digits:raise ValidationError(label+' inválida: hasta dos decimales.')
    return result

@require_http_methods(['GET','POST','PATCH'])
def assignments(request,pk=None):
    action='ver' if request.method=='GET' else 'editar' if pk else 'crear'
    denied=domain.gate(request,RESOURCE,action)
    if denied:return denied
    if request.method!='GET' and not manager(request.user):return api.error('Solo administrador y delegado pueden asignar metas.',403)
    if (pk and request.method=='POST') or (not pk and request.method=='PATCH'):return api.error('Método no permitido.',405)
    if request.method=='GET':
        qs=visible(request)
        if pk:
            obj=qs.filter(pk=pk).first()
            return api.ok(representation(obj)) if obj else api.error('Asignación no encontrada.',404)
        if 'fecha' in request.GET:
            try:day=date.fromisoformat(request.GET['fecha'])
            except (TypeError,ValueError):return api.error('Fecha de filtro inválida. Usa YYYY-MM-DD.')
            qs=qs.filter(periodo__fecha_inicio__lte=day,periodo__fecha_fin__gte=day)
        if 'disponibles' in request.GET:
            if request.GET['disponibles'] not in ['0','1']:return api.error('Filtro de disponibilidad inválido.')
            if request.GET['disponibles']=='1':qs=qs.filter(estado=True,item__estado=True,periodo__estado=True,periodo__cerrado=False,funcionario__is_active=True)
        for key in ['funcionario','periodo','item']:
            value=request.GET.get(key)
            if value:
                if not value.isdigit():return api.error('Filtro inválido.')
                qs=qs.filter(**{key+'_id':int(value)})
        if request.GET.get('q'):qs=qs.filter(Q(funcionario__username__icontains=request.GET['q'][:100])|Q(item__nombre__icontains=request.GET['q'][:100]))
        page=Paginator(qs,30).get_page(request.GET.get('page',1))
        d=api.active_delegation(request)
        people=Usuario.objects.filter(is_active=True).filter(Q(delegacion=d)|Q(delegaciones=d)).distinct() if manager(request.user) else Usuario.objects.filter(pk=request.user.pk)
        return api.ok(results=[representation(x) for x in page],count=page.paginator.count,page=page.number,total_pages=page.paginator.num_pages,puede_crear=manager(request.user) and api.allowed(request.user,RESOURCE,'crear'),puede_editar=manager(request.user) and api.allowed(request.user,RESOURCE,'editar'),opciones=dict(funcionarios=[dict(id=u.pk,nombre=u.get_full_name() or u.username) for u in people],items=list(ItemMeta.objects.filter(estado=True).values('id','nombre','tipo','unidad_medida','requiere_evidencia')),periodos=list(PeriodoGestion.objects.filter(estado=True).values('id','nombre','anio','numero','cerrado'))))
    try:
        data=api.body(request)
        if set(data)-{'funcionario','item','periodo','cantidad_objetivo','ponderacion','observacion','estado','_version'}:raise ValidationError('Hay campos no editables.')
        with transaction.atomic():
            old=visible(request).filter(pk=pk).first() if pk else None
            if pk and not old:return api.error('Asignación no encontrada.',404)
            if old and any(k in data and data[k]!=getattr(old,k+'_id') for k in ['funcionario','item','periodo']):raise ValidationError('Funcionario, meta y trimestre son inmutables; desactiva y crea otra asignación.')
            ids={k:getattr(old,k+'_id') if old else data.get(k) for k in ['funcionario','item','periodo']}
            if any(type(v) is not int for v in ids.values()):raise ValidationError('Selecciona funcionario, meta y trimestre.')
            # Todos los escritores bloquean periodo y usuario, incluso sin asignaciones previas.
            period=PeriodoGestion.objects.select_for_update().filter(pk=ids['periodo']).first()
            user=Usuario.objects.select_for_update().filter(pk=ids['funcionario']).first()
            if not period or not user:raise ValidationError('Referencias inexistentes.')
            if period.cerrado:raise ValidationError('El trimestre está cerrado; se conserva su historial.')
            quarter(period)
            if not period.estado:raise ValidationError('El trimestre está inactivo.')
            d=api.active_delegation(request)
            historical_deactivation=old is not None and data.get('estado') is False
            if not d or (not historical_deactivation and (not user.is_active or not Usuario.objects.filter(pk=user.pk).filter(Q(delegacion=d)|Q(delegaciones=d)).exists())):raise ValidationError('Funcionario inactivo o ajeno a la delegación.')
            item=ItemMeta.objects.filter(pk=ids['item']).first()
            if not item or (not item.estado and not old):raise ValidationError('Meta inexistente o inactiva.')
            obj=AsignacionMeta.objects.select_for_update().get(pk=old.pk) if old else AsignacionMeta(funcionario=user,item=item,periodo=period,delegacion=d,autor=request.user)
            before=representation(obj) if old else None
            if old and (type(data.get('_version')) is not int or data['_version']!=obj.version):return api.error('La asignación cambió. Recarga antes de guardar.',409)
            for k in ['cantidad_objetivo','ponderacion']:
                if k in data:setattr(obj,k,number(data[k],k,10 if k=='cantidad_objetivo' else 3))
            if obj.cantidad_objetivo is None or obj.cantidad_objetivo<=0:raise ValidationError('La cantidad objetivo debe ser positiva.')
            if obj.ponderacion is None or not 0<=obj.ponderacion<=100:raise ValidationError('La ponderación debe estar entre 0 y 100.')
            if 'estado' in data:
                if type(data['estado']) is not bool:raise ValidationError('Estado inválido.')
                obj.estado=data['estado']
            if 'observacion' in data:
                if not isinstance(data['observacion'],str) or len(data['observacion'])>2000:raise ValidationError('Observación inválida.')
                obj.observacion=data['observacion'].strip()
            if obj.estado:
                total=AsignacionMeta.objects.filter(funcionario=user,periodo=period,estado=True).exclude(pk=obj.pk).aggregate(total=Sum('ponderacion'))['total'] or Decimal('0')
                if total+obj.ponderacion>100:raise ValidationError('La suma de ponderaciones activas del funcionario y trimestre no puede superar 100 %.')
            if not old:obj.snapshot=dict(item_nombre=item.nombre,tipo=item.tipo,unidad_medida=item.unidad_medida,requiere_evidencia=item.requiere_evidencia,periodo_nombre=period.nombre,anio=period.anio,numero=period.numero)
            else:obj.version+=1
            obj.full_clean(validate_unique=False,validate_constraints=False);obj.save()
            after=representation(obj);api.record_event(request,RESOURCE,obj.pk,'editar' if old else 'crear',before,after)
            response=api.ok(after);response.status_code=200 if old else 201;return response
    except ValidationError as exc:return api.error('; '.join(exc.messages))
    except IntegrityError:return api.error('Ya existe una asignación de esta meta para el funcionario y trimestre.',409)

def bind_activity(activity,assignment_id):
    """Invocar dentro de transaction.atomic después de resolver autor, ítem y fecha."""
    if assignment_id in [None,'']:
        activity.asignacion_meta=None
        return
    if type(assignment_id) is not int:raise ValidationError('Asignación de meta inválida.')
    try:
        day=date.fromisoformat(activity.fecha) if isinstance(activity.fecha,str) else activity.fecha
        if type(day) is not date:raise ValueError
    except (ValueError,TypeError):raise ValidationError('La fecha de la actividad debe ser una fecha ISO válida.')
    prior=AsignacionMeta.objects.filter(pk=assignment_id).first()
    if not prior:raise ValidationError('La asignación de meta no existe.')
    period=PeriodoGestion.objects.select_for_update().get(pk=prior.periodo_id)
    Usuario.objects.select_for_update().get(pk=prior.funcionario_id)
    obj=AsignacionMeta.objects.select_for_update().get(pk=prior.pk)
    if period.cerrado or not period.estado or not obj.estado or obj.funcionario_id!=activity.autor_id or obj.item_id!=activity.item_id or obj.delegacion_id!=activity.delegacion_id or not period.fecha_inicio<=day<=period.fecha_fin:raise ValidationError('La asignación debe estar activa y corresponder al funcionario, meta, delegación y fecha del registro en un trimestre abierto.')
    quarter(period)
    activity.asignacion_meta=obj
