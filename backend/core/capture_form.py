"""Captura común; ficha social y seguimiento son extensiones de una actividad."""
import hashlib
import json
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction, IntegrityError
from django.views.decorators.http import require_POST
from . import local_api as api, domain_api as domain
from .capture_followup import fingerprint, create as followup, finish
from .models import Actividad

class Rejected(Exception):
 def __init__(self,response):self.response=response

def prior_response(request,key,digest):
 a=Actividad.objects.filter(clave_idempotencia=key).first()
 if a is None:return None
 if a.autor_id!=request.user.pk or a.delegacion_id!=api.active_delegation(request).pk or a.captura_hash!=digest:return api.error('La clave corresponde a otra captura.',409)
 return api.ok(domain.representation(a),is_duplicate_prevented=True)

@require_POST
def create(request):
 denied=domain.gate(request,'actividades','crear')
 if denied:return denied
 try:
  data=api.body(request)
  if set(data)-{'clave_idempotencia','actividad','social','nuevo_compromiso'}:raise ValidationError('Campos no permitidos en la captura.')
  key=data.get('clave_idempotencia')
  if not isinstance(key,str) or not key.strip() or len(key)>64:raise ValidationError('Falta una clave de captura válida.')
  values=data.get('actividad')
  if not isinstance(values,dict):raise ValidationError('Completa los datos del registro.')
  if set(values)-{'fecha','solicitud','accion','contacto','telefono','sector','item','junta_vecinos','profesional'}:raise ValidationError('La captura contiene campos no editables.')
  digest=fingerprint(data)
  previous=prior_response(request,key,digest)
  if previous:return previous
  social=data.get('social')
  if social is not None and not isinstance(social,dict):raise ValidationError('Datos sociales inválidos.')
  if social is not None and not api.allowed(request.user,'atenciones','crear'):raise PermissionDenied('No tienes permiso para registrar gestiones sociales.')
  with transaction.atomic():
   a=Actividad(autor=request.user,delegacion=api.active_delegation(request),cargo=request.user.cargo,
               plantilla=(request.user.cargo.planilla if request.user.cargo_id else '') or 'GENERAL',
               clave_idempotencia=key,captura_hash=digest,unidad=1)
   domain.apply_fields(request,'actividades',a,values)
   if social is not None:
    from .excel_support import SOCIAL_FIELDS
    allowed=set(SOCIAL_FIELDS)|{'tipo_atencion','sub_atencion','nuevo_caso','caso_social'}
    if set(social)-allowed:raise ValidationError('Campos sociales no permitidos.')
    social_data=dict(social,solicitante=a.contacto,descripcion=a.solicitud,telefono_solicitante=a.telefono,
                     gestion_realizada=a.accion,clave_idempotencia=hashlib.sha256((key+':social').encode()).hexdigest())
    response=api.create_attention(request,social_data)
    if response.status_code>=400:raise Rejected(response)
    a.atencion_id=json.loads(response.content)['data']['id']
   linked=followup(request,a,data.get('nuevo_compromiso'))
   if linked is not None:a.compromiso=linked
   from .catalog_history import activity
   a.catalogos_snapshot=activity(a);a.full_clean();a.save()
   from .auto_codes import operation_saved
   operation_saved(a,'actividades',request.user);finish(request,linked,a)
   if a.atencion_id:
    attention=a.atencion
    attention.compromiso=a.compromiso;attention.save(update_fields=['compromiso'])
    api.record_event(request,'atenciones',attention.pk,'vincular',None,{'actividad':a.pk,'compromiso':a.compromiso_id})
   api.record_event(request,'actividades',a.pk,'crear',None,domain.representation(a))
  response=api.ok(domain.representation(a));response.status_code=201;return response
 except Rejected as ex:return ex.response
 except PermissionDenied as ex:return api.error(str(ex),403)
 except IntegrityError:
  previous=prior_response(request,key,digest)
  return previous if previous else api.error('Conflicto al registrar. Recarga y vuelve a intentar.',409)
 except (ValidationError,ValueError,TypeError) as ex:return api.error('; '.join(ex.messages) if isinstance(ex,ValidationError) else 'Datos inválidos.')

from django.views.decorators.http import require_GET

@require_GET
def options(request):
 denied=domain.gate(request,'actividades','crear')
 if denied:return denied
 from django.db.models import Q
 from .models import Usuario,TipoAtencion,SubAtencion
 from .excel_support import items_for,GESTIONES
 d=api.active_delegation(request)
 social=api.allowed(request.user,'atenciones','crear')
 return api.ok(plantilla=(request.user.cargo.planilla if request.user.cargo_id else '') or 'GENERAL',
  items=list(items_for(request.user).values('id','codigo','nombre')),
  responsables=[{'id':u.pk,'nombre':u.get_full_name() or u.username} for u in Usuario.objects.filter(is_active=True).filter(Q(delegacion=d)|Q(delegaciones=d)).distinct()],
  tipos=list(TipoAtencion.objects.filter(estado=True).values('id','nombre')) if social else [],
  subtipos=list(SubAtencion.objects.filter(estado=True,tipo_atencion__estado=True).values('id','nombre','tipo_atencion')) if social else [],
  gestiones=GESTIONES if social else {})
