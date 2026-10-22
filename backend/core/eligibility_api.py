"""Catálogo explícito por delegación: publicar versiones sin reescribir historia."""
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction,IntegrityError
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from . import local_api as api, domain_api as domain,eligibility as service
from .capture_followup import fingerprint
from .models import ReglaActividad,ItemMeta,Actividad
from .eligibility_models import CLASIFICACIONES

RESOURCE='clasificacion-actividades'

def response(data=None,**extra):
    r=api.ok(data,**extra);r['Cache-Control']='private, no-store';return r

def replay(request,key,digest):
    r=ReglaActividad.objects.filter(clave_idempotencia=key).first()
    if r is None:return None
    if r.autor_id!=request.user.pk or r.delegacion_id!=api.active_delegation(request).pk or r.captura_hash!=digest:return api.error('La clave pertenece a otra definición.',409)
    return response(service.rule_data(r))

@require_http_methods(['GET','POST'])
def catalog(request,pk=None):
    denied=domain.gate(request,RESOURCE,'ver' if request.method=='GET' else 'configurar')
    if denied:return denied
    try:
        d=api.active_delegation(request)
        items=ItemMeta.objects.filter(estado=True)
        if request.method=='GET':
            if pk:
                item=items.filter(pk=pk).first()
                if not item:return api.error('Tipo de actividad no encontrado.',404)
                rules=ReglaActividad.objects.filter(delegacion=d,item=item)
                return response(dict(id=item.pk,nombre=item.nombre,codigo=item.codigo,regla=service.rule_data(rules.first()),historial=[service.rule_data(r) for r in rules]))
            if request.GET.get('q'):items=items.filter(Q(nombre__icontains=request.GET['q'][:100])|Q(codigo__icontains=request.GET['q'][:100]))
            page=Paginator(items.order_by('nombre','pk'),20).get_page(request.GET.get('page',1))
            return response(results=[dict(id=i.pk,nombre=i.nombre,codigo=i.codigo,regla=service.rule_data(service.current(d,i.pk))) for i in page],count=page.paginator.count,page=page.number,total_pages=page.paginator.num_pages,puede_configurar=api.allowed(request.user,RESOURCE,'configurar'),clasificaciones=CLASIFICACIONES)
        if not pk:return api.error('Selecciona el tipo de actividad.',405)
        data=api.body(request)
        if set(data)!={'_version','clasificacion','valida_para_puntuar','motivo','clave_idempotencia'}:raise ValidationError('Completa los datos de la regla; hay campos faltantes o no editables.')
        key=data['clave_idempotencia']
        if not isinstance(key,str) or not key.strip() or len(key)>64:raise ValidationError('Falta la clave de publicación.')
        digest=fingerprint(dict(data,item=pk));prior=replay(request,key,digest)
        if prior:return prior
        with transaction.atomic():
            item=items.select_for_update().filter(pk=pk).first()
            if not item:return api.error('Tipo de actividad no encontrado.',404)
            old=service.current(d,item.pk);previous=old.version if old else 0
            if type(data['_version']) is not int or data['_version']!=previous:return api.error('La regla cambió. Actualiza el catálogo antes de publicar.',409)
            kind=data['clasificacion'];enabled=data['valida_para_puntuar'];reason=data['motivo']
            if kind not in CLASIFICACIONES or type(enabled) is not bool:raise ValidationError('Clasificación o habilitación inválidas.')
            if enabled and kind!='Ejecución':raise ValidationError('Solo una ejecución válida puede habilitarse como potencialmente puntuable.')
            if not isinstance(reason,str) or not reason.strip() or len(reason)>2000:raise ValidationError('Indica un motivo de hasta 2000 caracteres.')
            rule=ReglaActividad(delegacion=d,item=item,version=previous+1,clasificacion=kind,valida_para_puntuar=enabled,motivo=reason.strip(),autor=request.user,clave_idempotencia=key,captura_hash=digest)
            rule.full_clean();rule.save();after=service.rule_data(rule);api.record_event(request,RESOURCE,rule.pk,'publicar',service.rule_data(old),after)
            r=response(after);r.status_code=201;return r
    except (ValidationError,IntegrityError,TypeError,ValueError) as e:
        if 'key' in locals() and 'digest' in locals():
            prior=replay(request,key,digest)
            if prior:return prior
        return api.error('; '.join(e.messages) if isinstance(e,ValidationError) else 'No fue posible publicar. Actualiza y revisa los datos.',409 if isinstance(e,IntegrityError) else 400)

@require_http_methods(['POST'])
def preview(request):
    denied=domain.gate(request,'actividades','crear')
    if denied:return denied
    try:
        data=api.body(request)
        if set(data)-{'item','contacto','telefono','beneficiario_usuario','rut_contacto','fecha'}:raise ValidationError('Campos no editables.')
        from .excel_support import items_for
        if type(data.get('item')) is not int:raise ValidationError('Selecciona el tipo de actividad.')
        item=items_for(request.user).filter(pk=data['item']).first()
        if not item:return api.error('Tipo de actividad no autorizado.',404)
        from datetime import date
        from .registration_limits import apply as apply_limits,TZ
        from django.utils import timezone
        selected_date=data.get('fecha') or str(timezone.localtime(timezone.now(),TZ).date())
        if not isinstance(selected_date,str):raise ValidationError('Fecha inválida.')
        obj=Actividad(delegacion=api.active_delegation(request),item=item,autor=request.user,fecha=date.fromisoformat(selected_date))
        for f,maxlen in [('contacto',200),('telefono',20),('rut_contacto',12)]:
            v=data.get(f,'')
            if not isinstance(v,str) or len(v)>maxlen:raise ValidationError('Datos de contacto inválidos.')
            setattr(obj,f,v.strip())
        if obj.rut_contacto:
            from .neighbors import normalize_rut
            obj.rut_contacto=normalize_rut(obj.rut_contacto)
        identifier=data.get('beneficiario_usuario')
        if identifier not in ['',None]:
            if type(identifier) is not int:raise ValidationError('Beneficiario inválido.')
            user=service.local_users(obj.delegacion).filter(pk=identifier).first()
            if not user:raise ValidationError('Beneficiario fuera de la delegación o inactivo.')
            obj.beneficiario_usuario=user
        return response(apply_limits(obj,service.evaluate_activity(obj,preview=True),preview=True))
    except (ValidationError,ValueError,TypeError) as e:return api.error('; '.join(e.messages) if isinstance(e,ValidationError) else 'Datos inválidos.')
