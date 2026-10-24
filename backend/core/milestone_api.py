"""Hitos por delegación, responsables y planificación interna sin puntuación."""
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from . import local_api as api, domain_api as domain
from .capture_followup import fingerprint
from .models import Hito, TareaHito, AvanceHito, Usuario, Compromiso
from .milestone_models import ESTADOS_HITO

CLOSED = ['Finalizado', 'Cancelado']
FIELDS = ['nombre','descripcion','fecha_inicio','fecha_termino','territorio','recursos','estado','recurrente','periodicidad','hito_anterior']
TASK_FIELDS = ['nombre','descripcion','responsable','fecha_limite']

def response(data=None, status=200, **extra):
    r=api.ok(data, **extra);r.status_code=status;r['Cache-Control']='private, no-store';return r

def manager(user):
    return bool(user.is_active and (user.is_superuser or (user.rol_id and user.rol.estado and user.rol.nombre.strip().casefold() in ['administrador', 'delegado'])))

def permitted(request, action):
    return api.allowed(request.user, 'hitos', action) and (action not in ['crear', 'editar', 'asignar'] or manager(request.user))

def visible(request):
    qs=Hito.objects.filter(delegacion=api.active_delegation(request))
    if not permitted(request,'ver_equipo'):qs=qs.filter(responsables=request.user)
    return qs.distinct()

def people(request):
    d=api.active_delegation(request)
    return Usuario.objects.filter(is_active=True).filter(Q(delegacion=d)|Q(delegaciones=d)).distinct()

def name(user):return user.get_full_name() or user.username

def task_data(t):
    return dict(id=t.pk, version=t.version, nombre=t.nombre, descripcion=t.descripcion,
        responsable=t.responsable_id, responsable_nombre=name(t.responsable),fecha_limite=str(t.fecha_limite),
        porcentaje=t.porcentaje, origen='Interno', compromiso=t.compromiso_id,
        estado_tubo=t.compromiso.estado if t.compromiso_id else None,
        avances=[dict(porcentaje=a.porcentaje,observacion=a.observacion,autor=name(a.autor),fecha=a.creado.isoformat()) for a in t.avances.select_related('autor')])

def hito_data(request,h,detail=False):
    data=api.serialize(h,FIELDS+['responsables']);data['responsables_nombres']=[dict(id=u.pk,nombre=name(u)) for u in h.responsables.all()]
    data['fecha_inicio']=str(h.fecha_inicio);data['fecha_termino']=str(h.fecha_termino) if h.fecha_termino else None
    data.update(delegacion=h.delegacion_id, puede_editar=permitted(request,'editar'),puede_asignar=permitted(request,'asignar'),puede_avanzar=permitted(request,'avanzar'),cerrado=h.estado in CLOSED)
    if detail:
        tasks=h.tareas.select_related('responsable','compromiso')
        if not permitted(request,'ver_equipo'):tasks=tasks.filter(responsable=request.user)
        data['tareas']=[task_data(t) for t in tasks]
    return data

def version(obj,data):
    if isinstance(data.get('_version'),bool) or data.pop('_version',None)!=obj.version:raise ValidationError('VERSION_CONFLICT')

def opened(h):
    if h.estado in CLOSED:raise ValidationError('El hito está finalizado o cancelado; su historial se conserva sin cambios.')

def resource_lines(value):
    if not isinstance(value,list) or len(value)>100:raise ValidationError('Indica hasta 100 recursos descriptivos.')
    result=[]
    for line in value:
        if not isinstance(line,dict) or set(line)-{'descripcion','cantidad','unidad'}:raise ValidationError('Recurso inválido.')
        text=line.get('descripcion');unit=line.get('unidad','unidades')
        if not isinstance(text,str) or not text.strip() or len(text)>250 or not isinstance(unit,str) or not unit.strip() or len(unit)>40:raise ValidationError('Indica descripción y unidad del recurso.')
        try:amount=Decimal(str(line.get('cantidad')))
        except InvalidOperation:raise ValidationError('Cantidad inválida.')
        if not amount.is_finite() or amount<=0 or amount>Decimal('999999999') or amount.as_tuple().exponent < -3:raise ValidationError('Cantidad positiva, hasta 999999999 y tres decimales.')
        result.append(dict(descripcion=text.strip(),cantidad=format(amount.normalize(),'f'),unidad=unit.strip()))
    return result

def apply_hito(request,h,data):
    if set(data)-set(FIELDS)-{'responsables'}:raise ValidationError('Hay campos no editables.')
    if h.pk and 'hito_anterior' in data:raise ValidationError('La realización anterior no se cambia.')
    selected=data.get('responsables',list(h.responsables.values_list('pk',flat=True)) if h.pk else [])
    if not isinstance(selected,list) or not selected or len(selected)>200 or any(type(i) is not int for i in selected):raise ValidationError('Selecciona al menos un responsable autorizado.')
    existing=list(h.responsables.values_list('pk',flat=True)) if h.pk else []
    eligible=people(request).values_list('pk',flat=True)
    users=list(Usuario.objects.filter(pk__in=selected).filter(Q(pk__in=eligible)|Q(pk__in=existing)))
    if len(users)!=len(set(selected)):raise ValidationError('Hay responsables inactivos o ajenos a la delegación.')
    if h.pk and h.tareas.exclude(responsable__in=users).exists():raise ValidationError('No puedes retirar a un responsable con tareas; reasígnalas primero.')
    for f,v in data.items():
        if f=='responsables':continue
        if f=='recursos':v=resource_lines(v)
        elif f=='recurrente':
            if type(v) is not bool:raise ValidationError('Recurrencia inválida.')
        elif f=='hito_anterior':
            if v in ['',None]:h.hito_anterior=None;continue
            if type(v) is not int:raise ValidationError('Realización anterior inválida.')
            prior=visible(request).filter(pk=v,recurrente=True).first()
            if not prior:raise ValidationError('La realización anterior debe ser recurrente y de esta delegación.')
            h.hito_anterior=prior;continue
        elif f=='fecha_termino' and v in ['',None]:v=None
        elif not isinstance(v,str):raise ValidationError('Los datos deben ser texto.')
        elif f not in ['fecha_inicio','fecha_termino']:v=v.strip()
        setattr(h,f,v)
    if not h.recurrente:h.periodicidad=''
    elif not h.periodicidad:raise ValidationError('Indica la periodicidad del evento recurrente.')
    h.full_clean()
    if h.fecha_termino and h.fecha_termino<h.fecha_inicio:raise ValidationError('El término no puede ser anterior al inicio.')
    if h.estado=='Finalizado' and h.pk:
        if h.tareas.exclude(porcentaje=100).exists() or h.tareas.filter(compromiso__isnull=False).exclude(compromiso__estado='Realizado').exists():raise ValidationError('Completa las tareas y cierra sus compromisos antes de finalizar.')
    if not h.pk and h.estado in CLOSED:raise ValidationError('Crea el hito en un estado de planificación o ejecución.')
    return users

def handle_error(ex):
    if isinstance(ex,PermissionDenied):return api.error(str(ex),403)
    if isinstance(ex,IntegrityError):return api.error('El registro cambió o ya existe. Actualiza la ficha.',409)
    if isinstance(ex,ValidationError):
        if ex.messages==['VERSION_CONFLICT']:return api.error('El registro cambió. Actualiza antes de guardar.',409)
        return api.error('; '.join(ex.messages))
    return api.error('Datos inválidos.')

@require_http_methods(['GET'])
def options(request):
    denied=domain.gate(request,'hitos','ver')
    if denied:return denied
    return response(puede_crear=permitted(request,'crear'), estados=ESTADOS_HITO, responsables=[dict(id=u.pk,nombre=name(u)) for u in people(request)] if permitted(request,'asignar') else [])

def replay(request,key,digest):
    h=Hito.objects.filter(clave_idempotencia=key).first()
    if h is None:return None
    if h.autor_id!=request.user.pk or h.delegacion_id!=api.active_delegation(request).pk or h.captura_hash!=digest:return api.error('La clave corresponde a otro hito.',409)
    return response(hito_data(request,h,True))

@require_http_methods(['GET','POST','PATCH'])
def records(request,pk=None):
    denied=domain.gate(request,'hitos','ver' if request.method=='GET' else 'crear' if request.method=='POST' else 'editar')
    if denied:return denied
    if request.method!='GET' and not manager(request.user):return api.error('Solo administrador y delegado pueden gestionar hitos.',403)
    if (request.method=='POST' and pk) or (request.method=='PATCH' and not pk):return api.error('Método no permitido.',405)
    try:
        if request.method=='GET':
            qs=visible(request)
            if pk:
                h=qs.filter(pk=pk).first()
                return response(hito_data(request,h,True)) if h else api.error('Hito no encontrado.',404)
            if request.GET.get('q'):qs=qs.filter(nombre__icontains=request.GET['q'][:100])
            if request.GET.get('estado'):qs=qs.filter(estado=request.GET['estado'])
            page=Paginator(qs,20).get_page(request.GET.get('page',1))
            return response(results=[hito_data(request,h) for h in page],count=page.paginator.count,total_pages=page.paginator.num_pages,page=page.number,puede_crear=permitted(request,'crear'))
        data=api.body(request)
        with transaction.atomic():
            if pk:
                h=visible(request).select_for_update().filter(pk=pk).first()
                if not h:return api.error('Hito no encontrado.',404)
                version(h,data);opened(h);before=hito_data(request,h)
                if 'responsables' in data and not permitted(request,'asignar'):raise PermissionDenied('No puedes asignar responsables.')
            else:
                if not permitted(request,'asignar'):raise PermissionDenied('No puedes asignar responsables.')
                key=data.pop('clave_idempotencia',None)
                if not isinstance(key,str) or not key.strip() or len(key)>64:raise ValidationError('Falta la clave del registro.')
                digest=fingerprint(data);prior=replay(request,key,digest)
                if prior:return prior
                h=Hito(delegacion=api.active_delegation(request),autor=request.user,clave_idempotencia=key,captura_hash=digest);before=None
            users=apply_hito(request,h,data)
            if pk:h.version+=1
            h.save();h.responsables.set(users)
            after=hito_data(request,h,True);api.record_event(request,'hitos',h.pk,'editar' if pk else 'crear',before,after)
            return response(after,status=200 if pk else 201)
    except (ValidationError,PermissionDenied,IntegrityError,TypeError,ValueError) as ex:
        if not pk and 'key' in locals() and 'digest' in locals():
            prior=replay(request,key,digest)
            if prior:return prior
        return handle_error(ex)

@require_http_methods(['POST','PATCH'])
def tasks(request,hito_id=None,pk=None,action=None):
    denied=domain.gate(request,'hitos','avanzar' if action=='avances' else 'asignar')
    if denied:return denied
    if action!='avances' and not manager(request.user):return api.error('Solo administrador y delegado pueden gestionar las actividades del hito.',403)
    if (pk is None and request.method!='POST') or (action and request.method!='POST') or (pk and not action and request.method!='PATCH'):return api.error('Método no permitido.',405)
    try:
        data=api.body(request)
        with transaction.atomic():
            # All mutation paths lock hito first, then tarea; closure cannot race an advance.
            h=visible(request).select_for_update().filter(pk=hito_id if hito_id else TareaHito.objects.filter(pk=pk).values('hito_id')[:1]).first()
            if not h:return api.error('Hito o actividad no encontrados.',404)
            opened(h)
            t=h.tareas.select_for_update().filter(pk=pk).first() if pk else None
            if pk and (not t or (action=='avances' and not permitted(request,'ver_equipo') and t.responsable_id!=request.user.pk)):return api.error('Actividad no encontrada.',404)
            before=task_data(t) if t else None
            if action=='tubo' and t.compromiso_id:return response(task_data(t))
            if t:version(t,data)
            if action=='avances':
                if set(data)!= {'porcentaje','observacion'} or type(data.get('porcentaje')) is not int or not 0<=data['porcentaje']<=100 or not isinstance(data.get('observacion'),str) or not data['observacion'].strip() or len(data['observacion'])>2000:raise ValidationError('Indica un avance de 0 a 100 y una observación de hasta 2000 caracteres.')
                t.porcentaje=data['porcentaje'];t.version+=1;t.save()
                AvanceHito.objects.create(tarea=t,autor=request.user,porcentaje=t.porcentaje,observacion=data['observacion'].strip())
            elif action=='tubo':
                if data:raise ValidationError('Hay campos no editables.')
                if not api.allowed(request.user,'compromisos','crear'):raise PermissionDenied('No tienes permiso para crear seguimiento en el tubo.')
                if t.fecha_limite<timezone.localdate():raise ValidationError('El plazo de la actividad ya venció. Actualízalo antes de enviarla al tubo.')
                if not people(request).filter(pk=t.responsable_id).exists():raise ValidationError('El responsable está inactivo o fuera de la delegación. Reasigna la actividad antes de enviarla al tubo.')
                c=Compromiso(delegacion=h.delegacion,autor=request.user,responsable=t.responsable,fecha_solicitud=timezone.localdate(),fecha_comprometida=t.fecha_limite,descripcion=t.nombre+'\n'+t.descripcion,solicitante=('Hito interno: '+h.nombre)[:200],sector=h.territorio,origen='Interno')
                c.full_clean();c.save()
                from .auto_codes import operation_saved
                operation_saved(c,'compromisos',request.user)
                t.compromiso=c;t.version+=1;t.save()
                api.record_event(request,'compromisos',c.pk,'crear',None,dict(hito=h.pk,tarea=t.pk,origen='Interno',folio=c.folio))
            else:
                if set(data)-set(TASK_FIELDS):raise ValidationError('Hay campos no editables.')
                if not t:t=TareaHito(hito=h,autor=request.user)
                for f,v in data.items():
                    if f=='responsable':
                        if type(v) is not int or not h.responsables.filter(pk=v,is_active=True).exists() or not people(request).filter(pk=v).exists():raise ValidationError('Selecciona un responsable activo del hito.')
                        if t.compromiso_id and v!=t.responsable_id:raise ValidationError('Reasigna el compromiso desde el tubo para mantener un único seguimiento.')
                        t.responsable_id=v
                    else:
                        if not isinstance(v,str):raise ValidationError('Datos inválidos.')
                        if t.compromiso_id and f=='fecha_limite' and v!=str(t.fecha_limite):raise ValidationError('Cambia el plazo desde el tubo.')
                        setattr(t,f,v.strip())
                t.full_clean()
                if pk:t.version+=1
                t.save()
            after=task_data(t);api.record_event(request,'hitos-tareas',t.pk,action or ('editar' if pk else 'crear'),before,after)
            return response(after,status=201 if not pk or action=='tubo' else 200)
    except (ValidationError,PermissionDenied,IntegrityError,TypeError,ValueError) as ex:return handle_error(ex)


def validate_commitment_edit(request,obj,data):
    task=getattr(obj,'tarea_hito',None)
    if task is None:return
    opened(task.hito)
    allowed={'_version','estado','observacion'}
    if permitted(request,'asignar'):allowed|={'descripcion','responsable','fecha_comprometida','area_apoyo'}
    if set(data)-allowed:raise ValidationError('El compromiso pertenece a un hito interno. Solo su gestor reasigna responsables o plazos; el origen interno se conserva.')
    if 'responsable' in data and (not task.hito.responsables.filter(pk=data['responsable'],is_active=True).exists() or not people(request).filter(pk=data['responsable']).exists()):raise ValidationError('El responsable debe pertenecer al hito.')

def sync_commitment(obj):
    task=getattr(obj,'tarea_hito',None)
    if task is not None and (task.responsable_id!=obj.responsable_id or task.fecha_limite!=obj.fecha_comprometida):
        task.responsable=obj.responsable;task.fecha_limite=obj.fecha_comprometida;task.version+=1;task.save()


def lock_commitment_hito(request,pk):
    h=Hito.objects.filter(tareas__compromiso_id=pk,delegacion=api.active_delegation(request)).select_for_update().first()
    if h:opened(h)
