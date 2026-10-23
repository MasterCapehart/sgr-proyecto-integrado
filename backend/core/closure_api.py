"""Controles y evidencia operativa local con ámbito y permisos por operación."""
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from . import local_api as api, domain_api as domain
from .models import (VersionCatalogo, PoliticaOperativa, AlertaLocal, Compromiso, Actividad, Evidencia, RevisionEvidencia, SeguimientoCompromiso)
from .operating_policy import STATES, current, permissions_snapshot
from .catalog_history import CATALOGS, catalog

def reason(data,key='motivo'):
    text=data.get(key)
    if not isinstance(text,str) or not text.strip() or len(text)>2000:raise ValidationError('Indica un motivo de hasta 2000 caracteres.')
    return text.strip()

@require_http_methods(['GET'])
def history(request,resource,pk):
    denied=domain.gate(request,resource,'ver')
    if denied:return denied
    if resource not in CATALOGS:return api.error('Este recurso no tiene historial de catálogo.',404)
    model=api.RESOURCES[resource][0];qs=model.objects.all()
    if resource=='delegaciones':qs=api.delegations(request.user)
    obj=qs.filter(pk=pk).first()
    if not obj:return api.error('Catálogo no encontrado.',404)
    rows=[{'version':x.version,'datos':x.datos,'fecha':x.fecha.isoformat(),'autor':x.autor.username if x.autor_id else None,'observada':x.observada} for x in VersionCatalogo.objects.filter(recurso=resource,registro=pk).select_related('autor')]
    if not any(r['version']==obj.version for r in rows):rows.insert(0,{'version':obj.version,'datos':catalog(obj),'fecha':None,'autor':None,'observada':True})
    return api.ok(results=rows,message='Las versiones observadas no garantizan la etiqueta original de un registro anterior a esta captura.')

@require_http_methods(['GET','POST'])
def governance(request):
    denied=domain.gate(request,'gobierno','configurar' if request.method=='POST' else 'ver')
    if denied:return denied
    if request.method=='GET':return api.ok({'politica':current(),'roles':permissions_snapshot(),'permisos_disponibles':api.PERMISSIONS,'fuente':'PDF segunda evaluación B5/AGE-03. La validación local no sustituye aceptación funcional.'})
    try:
        data=api.body(request);motivo=reason(data);transitions=data.get('transiciones');validated=data.get('validar',False)
        if not isinstance(validated,bool):return api.error('La confirmación debe ser booleana.')
        if not isinstance(transitions,dict) or set(transitions)!=set(STATES):return api.error('Configura los cuatro estados de agenda.')
        for state,targets in transitions.items():
            if not isinstance(targets,list) or len(targets)!=len(set(str(x) for x in targets)) or any(not isinstance(x,str) or x not in STATES or x==state for x in targets):return api.error('Transiciones inválidas.')
        if transitions['Realizado']:return api.error('La reapertura usa una operación separada y autorizada; Realizado no tiene salidas ordinarias.')
        with transaction.atomic():
            # Serializa los cambios incluso antes de que exista la primera política.
            from .models import Delegacion
            Delegacion.objects.select_for_update().order_by('pk').first()
            latest=current()
            if data.get('_version')!=latest['version']:return api.error('La política cambió. Recarga antes de guardar.',409)
            roles=permissions_snapshot()
            if validated and data.get('roles_versiones')!={str(x['id']):x['version'] for x in roles}:return api.error('Los permisos cambiaron. Revísalos antes de validar.',409)
            row=PoliticaOperativa.objects.create(version=latest['version']+1,transiciones=transitions,motivo=motivo,autor=request.user,validada=validated,permisos_snapshot=roles)
            api.record_event(request,'gobierno',row.pk,'validar_local' if validated else 'proponer',latest,{'politica':current(),'roles':roles})
        return api.ok({'politica':current(),'roles':roles})
    except (ValidationError,ValueError,TypeError) as ex:return api.error('; '.join(ex.messages) if isinstance(ex,ValidationError) else 'Configuración inválida.')

@transaction.atomic
def sync_alerts(request):
    if not api.allowed(request.user,'alertas','ver'):return
    # Mismo orden de bloqueo que las mutaciones: compromiso o actividad antes de evidencia.
    if api.allowed(request.user,'compromisos','ver'):
        list(domain.scoped(request,'compromisos').select_for_update().order_by('pk'))
    if api.allowed(request.user,'evidencias','ver'):
        activity_ids=domain.scoped(request,'evidencias').values_list('actividad_id',flat=True)
        list(Actividad.objects.filter(pk__in=activity_ids).select_for_update().order_by('pk'))
    active_keys=[];visible={}
    for resource in ['compromisos','evidencias']:
        if not api.allowed(request.user,resource,'ver'):visible[resource]=[];continue
        qs=domain.scoped(request,resource);visible[resource]=list(qs.values_list('pk',flat=True))
        if resource=='compromisos':
            for c in qs.filter(fecha_comprometida__lt=timezone.localdate()).exclude(estado='Realizado'):
                key=f'compromiso:{c.pk}:{c.fecha_comprometida}:{c.cierres.count()}'
                obj,_=AlertaLocal.objects.get_or_create(clave=key,defaults={'delegacion':c.delegacion,'responsable':c.responsable,'recurso':resource,'registro':c.pk,'tipo':'vencimiento','motivo':f'Compromiso sin realizar; fecha comprometida {c.fecha_comprometida}.','fecha_referencia':c.fecha_comprometida})
                active_keys.append(key)
                if obj.responsable_id!=c.responsable_id:obj.responsable=c.responsable;obj.version+=1;obj.save(update_fields=['responsable','version'])
        else:
            for e in qs.filter(estado='Pendiente',siguiente_version__isnull=True):
                key=f'evidencia:{e.pk}'
                AlertaLocal.objects.get_or_create(clave=key,defaults={'delegacion':e.delegacion,'responsable':e.actividad.autor,'recurso':resource,'registro':e.pk,'tipo':'evidencia_pendiente','motivo':f'Evidencia {e.nombre_archivo} pendiente de revisión.','fecha_referencia':timezone.localtime(e.creado).date()})
                active_keys.append(key)
    scope=Q(pk__in=[])
    for resource,ids in visible.items():scope|=Q(recurso=resource,registro__in=ids)
    for obj in AlertaLocal.objects.filter(scope,delegacion=api.active_delegation(request)):
        wanted=obj.clave in active_keys
        if obj.activa!=wanted:
            obj.activa=wanted;obj.resuelta_en=None if wanted else timezone.now();obj.version+=1;obj.save(update_fields=['activa','resuelta_en','version'])

def alert_scope(request):
    scope=Q(pk__in=[])
    for resource in ['compromisos','evidencias']:
        if api.allowed(request.user,resource,'ver'):scope|=Q(recurso=resource,registro__in=domain.scoped(request,resource).values('pk'))
    return AlertaLocal.objects.filter(scope,delegacion=api.active_delegation(request)).select_related('responsable','revisada_por')

def alert_data(a):
    return {'id':a.pk,'version':a.version,'tipo':a.tipo,'recurso':a.recurso,'registro':a.registro,'motivo':a.motivo,'responsable':a.responsable.get_full_name() or a.responsable.username,'fecha':a.fecha.isoformat(),'fecha_referencia':str(a.fecha_referencia) if a.fecha_referencia else None,'activa':a.activa,'revisada':a.revisada_en is not None,'revisada_por':a.revisada_por.username if a.revisada_por_id else None,'revisada_en':a.revisada_en.isoformat() if a.revisada_en else None,'resuelta_en':a.resuelta_en.isoformat() if a.resuelta_en else None,'enlace':f'/pages/compromiso-detalle.html?id={a.registro}' if a.recurso=='compromisos' else f'/pages/evidencias.html?registro={a.registro}'}

@require_http_methods(['GET'])
def alerts(request):
    denied=domain.gate(request,'alertas','ver')
    if denied:return denied
    sync_alerts(request);qs=alert_scope(request)
    if request.GET.get('activa') in ['si','no']:qs=qs.filter(activa=request.GET['activa']=='si')
    if request.GET.get('revisada') in ['si','no']:qs=qs.filter(revisada_en__isnull=request.GET['revisada']=='no')
    try:page=int(request.GET.get('page',1))
    except ValueError:return api.error('Página inválida.')
    pager=Paginator(qs,20)
    if page<1 or page>pager.num_pages:return api.error('Página inexistente.',404)
    return api.ok(results=[alert_data(a) for a in pager.page(page)],count=pager.count,page=page,total_pages=pager.num_pages,message='Detección local al consultar; no implica envío de correo ni monitoreo en segundo plano.')

@require_http_methods(['POST'])
def mark_alert(request,pk):
    denied=domain.gate(request,'alertas','revisar')
    if denied:return denied
    try:
        data=api.body(request)
        with transaction.atomic():
            obj=alert_scope(request).select_for_update().filter(pk=pk).first()
            if not obj:return api.error('Alerta no encontrada.',404)
            conflict=domain.validate_version(obj,data)
            if conflict:return conflict
            previous=alert_data(obj)
            if not obj.revisada_en:obj.revisada_por=request.user;obj.revisada_en=timezone.now();obj.version+=1;obj.save()
            api.record_event(request,'alertas',obj.pk,'revisar',previous,alert_data(obj))
        return api.ok(alert_data(obj))
    except (ValidationError,ValueError,TypeError):return api.error('Solicitud inválida.')

@require_http_methods(['POST'])
def annul(request,pk):
    denied=domain.gate(request,'evidencias','anular')
    if denied:return denied
    try:
        data=api.body(request);motivo=reason(data)
        with transaction.atomic():
            candidate=domain.scoped(request,'evidencias').filter(pk=pk).values('actividad_id').first()
            if not candidate:return api.error('Evidencia no encontrada.',404)
            from .performance import lock_periods
            lock_periods(candidate['actividad_id'])
            activity=Actividad.objects.select_for_update().get(pk=candidate['actividad_id'])
            obj=domain.scoped(request,'evidencias').select_for_update().filter(pk=pk).first()
            if not obj:return api.error('Evidencia no encontrada.',404)
            conflict=domain.validate_version(obj,data)
            if conflict:return conflict
            if obj.estado=='Anulada':return api.error('Esta evidencia ya está anulada.',409)
            before=domain.representation(obj);obj.estado='Anulada';obj.version+=1;obj.save()
            RevisionEvidencia.objects.create(evidencia=obj,autor=request.user,decision='Anulada',observacion=motivo,version_evidencia=obj.version)
            activity=Actividad.objects.select_for_update().get(pk=obj.actividad_id)
            states=set(activity.evidencias.filter(siguiente_version__isnull=True).exclude(estado='Anulada').values_list('estado',flat=True))
            activity.estado='Validada' if states=={'Aprobada'} else 'Rechazada' if 'Rechazada' in states else 'Corrección' if not states or 'Corrección' in states else 'Pendiente';activity.version+=1;activity.save()
            AlertaLocal.objects.filter(recurso='evidencias',registro=obj.pk,activa=True).update(activa=False,resuelta_en=timezone.now())
            api.record_event(request,'evidencias',obj.pk,'anular',before,domain.representation(obj))
        return api.ok(domain.representation(obj))
    except (ValidationError,ValueError,TypeError):return api.error('Datos de anulación inválidos.')

@require_http_methods(['POST'])
def reopen(request,pk):
    denied=domain.gate(request,'compromisos','reabrir')
    if denied:return denied
    try:
        data=api.body(request);motivo=reason(data)
        with transaction.atomic():
            from .milestone_api import lock_commitment_hito
            lock_commitment_hito(request,pk)
            obj=domain.scoped(request,'compromisos').select_for_update().filter(pk=pk).first()
            if not obj:return api.error('Compromiso no encontrado.',404)
            conflict=domain.validate_version(obj,data)
            if conflict:return conflict
            if obj.estado!='Realizado':return api.error('Solo se reabre un compromiso realizado.')
            before=domain.representation(obj);obj.estado='En proceso';obj.cierre_actual=None;obj.version+=1;obj.save()
            SeguimientoCompromiso.objects.create(compromiso=obj,autor=request.user,estado_anterior='Realizado',estado_nuevo=obj.estado,observacion='Reapertura: '+motivo,responsable_anterior=obj.responsable,responsable_nuevo=obj.responsable,fecha_anterior=obj.fecha_comprometida,fecha_nueva=obj.fecha_comprometida)
            api.record_event(request,'compromisos',obj.pk,'reabrir',before,domain.representation(obj))
        return api.ok(domain.representation(obj))
    except (ValidationError,ValueError,TypeError):return api.error('Datos de reapertura inválidos.')
