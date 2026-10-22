"""Calendarios y ausencias con permisos, versiones, auditoría y cierre protegido."""
from django.core.exceptions import ValidationError
from django.db import transaction,IntegrityError
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from . import local_api as api,domain_api as domain,absences as service
from .models import CalendarioFuncionario,AusenciaFuncionario,Usuario,PeriodoGestion,EventoLocal
from .absence_models import JORNADAS,TIPOS

def manager(u):return bool(u.is_active and (u.is_superuser or (u.rol_id and u.rol.estado and u.rol.nombre.strip().casefold() in ['administrador','delegado'])))
def can_manage(u):return manager(u) and api.allowed(u,'ausencias','gestionar')
def people(request):
    d=api.active_delegation(request);qs=Usuario.objects.filter(is_active=True).filter(Q(delegacion=d)|Q(delegaciones=d)).distinct()
    return qs if manager(request.user) and api.allowed(request.user,'ausencias','ver_equipo') else qs.filter(pk=request.user.pk)
def gate(request,write=False):
    denied=domain.gate(request,'ausencias','gestionar' if write else 'ver')
    if denied:return denied
    if write and not can_manage(request.user):return api.error('Solo administrador y delegado pueden gestionar ausencias y calendarios.',403)
def identifier(v):
    if isinstance(v,bool) or not str(v).isdigit():raise ValidationError('Referencia inválida.')
    return int(v)
def reason(v):
    if not isinstance(v,str) or not v.strip() or len(v)>500:raise ValidationError('Indica un motivo administrativo de hasta 500 caracteres, sin diagnósticos ni datos clínicos.')
    return v.strip()
def period(pk,lock=False):
    p=(PeriodoGestion.objects.select_for_update() if lock else PeriodoGestion.objects).filter(pk=identifier(pk)).first()
    if not p:raise ValidationError('Período no encontrado.')
    if (p.fecha_fin-p.fecha_inicio).days>3660:raise ValidationError('El calendario admite períodos de hasta diez años.')
    return p
def opened(p):
    if p.cerrado or not p.estado:raise ValidationError('El período debe estar activo y abierto; requiere reapertura autorizada para corregir.')
def history(resource,pk):
    return [dict(version=e.despues.get('version'),fecha=e.fecha.isoformat(),autor=e.usuario_id,accion=e.accion,datos=e.despues) for e in EventoLocal.objects.filter(recurso=resource,registro=pk).order_by('-pk')[:100]]
def calendar_data(c):
    return dict(id=c.pk,version=c.version,funcionario=c.funcionario_id,periodo=c.periodo_id,semana=c.semana,no_laborables=c.no_laborables,metas_prorrateables=c.metas_prorrateables,motivo=c.motivo)
def absence_data(a,detail=False):
    r=dict(id=a.pk,version=a.version,calendario=a.calendario_id,tipo=a.tipo,inicio=str(a.inicio),fin=str(a.fin),jornada=a.jornada,justificacion=a.justificacion,estado=a.estado,autor=a.autor_id)
    if detail:r['historial']=history('ausencias',a.pk)
    return r
def failure(ex):
    if isinstance(ex,IntegrityError):return api.error('Ya existe un calendario o el registro cambió. Recarga antes de continuar.',409)
    return api.error('; '.join(ex.messages) if isinstance(ex,ValidationError) else 'Datos inválidos.')
@require_http_methods(['GET'])
def options(request):
    denied=gate(request)
    if denied:return denied
    return api.ok(funcionarios=[dict(id=u.pk,nombre=u.get_full_name() or u.username) for u in people(request)],periodos=list(PeriodoGestion.objects.order_by('-fecha_inicio').values('id','nombre','fecha_inicio','fecha_fin','cerrado','estado')),jornadas=JORNADAS,tipos=TIPOS,puede_gestionar=can_manage(request.user))
@require_http_methods(['GET'])
def overview(request):
    denied=gate(request)
    if denied:return denied
    try:
        u=people(request).filter(pk=identifier(request.GET.get('funcionario'))).first()
        if not u:return api.error('Funcionario no encontrado en tu contexto autorizado.',404)
        p=period(request.GET.get('periodo'));cal=CalendarioFuncionario.objects.filter(delegacion=api.active_delegation(request),funcionario=u,periodo=p).first()
        return api.ok(service.summary(api.active_delegation(request),u,p),calendario=calendar_data(cal) if cal else None,ausencias=[absence_data(a,True) for a in cal.ausencias.order_by('-inicio','-pk')] if cal else [],puede_gestionar=can_manage(request.user) and not p.cerrado and p.estado)
    except (ValidationError,ValueError,TypeError) as ex:return failure(ex)
@require_http_methods(['POST','PATCH'])
def calendars(request,pk=None):
    denied=gate(request,True)
    if denied:return denied
    if (request.method=='PATCH')!=bool(pk):return api.error('Método no permitido.',405)
    try:
        data=api.body(request)
        if set(data)-{'funcionario','periodo','semana','no_laborables','metas_prorrateables','confirmado','motivo','_version'}:raise ValidationError('Campos no permitidos.')
        with transaction.atomic():
            old=CalendarioFuncionario.objects.filter(pk=pk,delegacion=api.active_delegation(request)).first() if pk else None
            if pk and not old:return api.error('Calendario no encontrado.',404)
            p=period(old.periodo_id if old else data.get('periodo'),True);opened(p)
            u=people(request).filter(pk=old.funcionario_id if old else identifier(data.get('funcionario'))).first()
            if not u:return api.error('Funcionario no encontrado.',404)
            if old:
                old=CalendarioFuncionario.objects.select_for_update().get(pk=pk)
                denied=domain.validate_version(old,data)
                if denied:return denied
                if ('periodo' in data and identifier(data['periodo'])!=p.pk) or ('funcionario' in data and identifier(data['funcionario'])!=u.pk):raise ValidationError('El funcionario y período quedan fijos.')
            c=old or CalendarioFuncionario(delegacion=api.active_delegation(request),funcionario=u,periodo=p,autor=request.user)
            before=calendar_data(c) if old else None
            if data.get('confirmado') is not True:raise ValidationError('Confirma que revisaste la jornada y los días no laborables del período.')
            week=data.get('semana',c.semana);off=data.get('no_laborables',c.no_laborables);metas=data.get('metas_prorrateables',c.metas_prorrateables)
            if not isinstance(week,list) or len(week)!=7 or any(v not in JORNADAS for v in week):raise ValidationError('Indica la jornada de cada día de lunes a domingo.')
            if not isinstance(off,list) or len(off)>3660:raise ValidationError('Días no laborables inválidos.')
            for d in off:
                if not isinstance(d,str) or len(d)!=10 or not p.fecha_inicio<=service.parse(d)<=p.fecha_fin:raise ValidationError('Los días no laborables deben pertenecer al período.')
            if not isinstance(metas,list) or any(type(v) is not int for v in metas) or len(metas)!=len(set(metas)) or set(metas)-set(service.meta_rows(u,p).values_list('pk',flat=True)):raise ValidationError('Selecciona metas vigentes del funcionario y período.')
            c.semana=week;c.no_laborables=sorted(set(off));c.metas_prorrateables=metas;c.motivo=reason(data.get('motivo'));c.version+=1 if old else 0;c.full_clean();c.save()
            api.record_event(request,'calendarios-ausencias',c.pk,'editar' if old else 'crear',before,calendar_data(c))
        r=api.ok(calendar_data(c));r.status_code=200 if pk else 201;return r
    except (ValidationError,ValueError,TypeError,IntegrityError) as ex:return failure(ex)
@require_http_methods(['POST','PATCH'])
def records(request,pk=None):
    denied=gate(request,True)
    if denied:return denied
    if (request.method=='PATCH')!=bool(pk):return api.error('Método no permitido.',405)
    try:
        data=api.body(request)
        if set(data)-{'calendario','tipo','inicio','fin','jornada','justificacion','estado','_version'}:raise ValidationError('Campos no permitidos.')
        with transaction.atomic():
            old=AusenciaFuncionario.objects.filter(pk=pk,delegacion=api.active_delegation(request)).first() if pk else None
            if pk and not old:return api.error('Ausencia no encontrada.',404)
            cal=CalendarioFuncionario.objects.filter(pk=old.calendario_id if old else identifier(data.get('calendario')),delegacion=api.active_delegation(request),funcionario__in=people(request)).first()
            if not cal:return api.error('Calendario no encontrado.',404)
            p=period(cal.periodo_id,True);opened(p)
            cal=CalendarioFuncionario.objects.select_for_update().get(pk=cal.pk)
            if old:
                old=AusenciaFuncionario.objects.select_for_update().get(pk=pk)
                denied=domain.validate_version(old,data)
                if denied:return denied
                if 'calendario' in data and identifier(data['calendario'])!=cal.pk:raise ValidationError('El calendario de la ausencia queda fijo.')
            a=old or AusenciaFuncionario(calendario=cal,autor=request.user,delegacion=cal.delegacion)
            before=absence_data(a) if old else None
            for key in ['tipo','jornada','estado']:
                if key in data:
                    if not isinstance(data[key],str):raise ValidationError('Datos de ausencia inválidos.')
                    setattr(a,key,data[key])
            for key in ['inicio','fin']:
                if key in data:
                    if not isinstance(data[key],str) or len(data[key])!=10:raise ValidationError('Fecha inválida.')
                    setattr(a,key,service.parse(data[key]))
            a.justificacion=reason(data.get('justificacion'));a.version+=1 if old else 0;a.full_clean()
            if a.inicio>a.fin or a.fin<p.fecha_inicio or a.inicio>p.fecha_fin:raise ValidationError('La ausencia debe solaparse con el período y sus fechas deben estar ordenadas.')
            a.save();api.record_event(request,'ausencias',a.pk,'editar' if old else 'crear',before,absence_data(a))
        r=api.ok(absence_data(a,True));r.status_code=200 if pk else 201;return r
    except (ValidationError,ValueError,TypeError,IntegrityError) as ex:return failure(ex)
