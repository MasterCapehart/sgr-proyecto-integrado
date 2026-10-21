"""Directorio vecinal acotado a la delegación activa y al permiso de captura."""
import re
from django.core.exceptions import ValidationError
from django.db import IntegrityError,transaction
from django.views.decorators.http import require_POST
from . import local_api as api,domain_api as domain
from .capture_followup import fingerprint
from .models import Vecino

FIELDS=('nombre','rut','telefono','sector','junta_vecinos')

def normalize_rut(value):
 if value in ('',None):return ''
 if not isinstance(value,str):raise ValidationError('El RUN debe ser texto.')
 raw=re.sub(r'[.\s-]','',value).upper()
 if not re.fullmatch(r'\d{7,8}[0-9K]',raw):raise ValidationError('RUN inválido. Revisa número y dígito verificador.')
 number,digit=str(int(raw[:-1])),raw[-1]
 if not 7<=len(number)<=8:raise ValidationError('RUN inválido.')
 total=sum(int(n)*(2+i%6) for i,n in enumerate(reversed(number)));expected=11-total%11
 expected='0' if expected==11 else 'K' if expected==10 else str(expected)
 if digit!=expected:raise ValidationError('El dígito verificador del RUN no es válido.')
 return number+'-'+digit

def representation(obj):return dict(id=obj.pk,**{field:getattr(obj,field) or '' for field in FIELDS})

def prior(request,key,digest):
 obj=Vecino.objects.filter(clave_idempotencia=key).first()
 if obj is None:return None
 if obj.creado_por_id!=request.user.pk or obj.delegacion_id!=api.active_delegation(request).pk or obj.captura_hash!=digest:return api.error('La clave corresponde a otro registro vecinal.',409)
 return api.ok(representation(obj),is_duplicate_prevented=True)

@require_POST
def search(request):
 denied=domain.gate(request,'actividades','crear')
 if denied:return denied
 try:
  data=api.body(request);q=data.get('q','')
  if set(data)-{'q'} or not isinstance(q,str) or len(q)>100:raise ValidationError('Búsqueda inválida.')
  q=' '.join(q.split());qs=Vecino.objects.filter(delegacion=api.active_delegation(request))
  if len(q)<3:return api.ok(results=[],has_more=False,message='Escribe al menos tres letras del nombre o el RUN completo.')
  if re.fullmatch(r'[\d.\sKk-]+',q):
   try:rut=normalize_rut(q)
   except ValidationError:return api.ok(results=[],has_more=False,message='Revisa el RUN completo y su dígito verificador.')
   qs=qs.filter(rut=rut)
  else:qs=qs.filter(nombre__icontains=q)
  rows=list(qs[:21]);response=api.ok(results=[representation(v) for v in rows[:20]],has_more=len(rows)>20);response['Cache-Control']='private, no-store';return response
 except (ValidationError,TypeError,ValueError) as ex:return api.error('; '.join(ex.messages) if isinstance(ex,ValidationError) else 'Búsqueda inválida.')

@require_POST
def create(request):
 denied=domain.gate(request,'actividades','crear')
 if denied:return denied
 try:
  data=api.body(request)
  if set(data)-set(FIELDS)-{'clave_idempotencia'}:raise ValidationError('Hay campos no editables.')
  key=data.get('clave_idempotencia')
  if not isinstance(key,str) or not key.strip() or len(key)>64:raise ValidationError('Falta una clave válida de registro vecinal.')
  if any(not isinstance(data.get(f,''),str) for f in FIELDS):raise ValidationError('Los datos del vecino deben ser texto.')
  values={f:data.get(f,'').strip() for f in FIELDS};values['nombre']=' '.join(values['nombre'].split());values['rut']=normalize_rut(values['rut'])
  if len(values['nombre'])<2:raise ValidationError('Indica el nombre del vecino.')
  if values['telefono'] and not re.fullmatch(r'\+?[0-9 ()-]{8,20}',values['telefono']):raise ValidationError('Teléfono inválido.')
  digest=fingerprint(values);previous=prior(request,key,digest)
  if previous:return previous
  d=api.active_delegation(request)
  with transaction.atomic():
   obj=Vecino(delegacion=d,creado_por=request.user,clave_idempotencia=key,captura_hash=digest,**{**values,'rut':values['rut'] or None})
   obj.full_clean();obj.save();api.record_event(request,'vecinos',obj.pk,'crear',None,representation(obj))
  response=api.ok(representation(obj));response.status_code=201;return response
 except IntegrityError:
  previous=prior(request,key,digest)
  return previous if previous else api.error('El RUN o la solicitud ya fueron registrados. Busca al vecino antes de continuar.',409)
 except ValidationError as ex:
  if 'digest' in locals():
   previous=prior(request,key,digest)
   if previous:return previous
   if values['rut'] and Vecino.objects.filter(delegacion=d,rut=values['rut']).exists():return api.error('Este RUN ya está registrado en la delegación.',409)
  return api.error('; '.join(ex.messages))
 except (TypeError,ValueError):return api.error('Datos inválidos.')

def bind(request,activity,identifier):
 if identifier in ('',None):return
 if isinstance(identifier,bool) or not str(identifier).isdigit():raise ValidationError('Selecciona un vecino válido.')
 obj=Vecino.objects.filter(pk=identifier,delegacion=api.active_delegation(request)).first()
 if obj is None:return False
 if ' '.join(activity.contacto.casefold().split())!=' '.join(obj.nombre.casefold().split()):raise ValidationError('El nombre no coincide con el vecino seleccionado. Cambia la selección para registrar otra persona.')
 if activity.rut_contacto and activity.rut_contacto!=(obj.rut or ''):raise ValidationError('El RUN no coincide con el vecino seleccionado.')
 activity.vecino=obj;activity.contacto=obj.nombre;activity.rut_contacto=obj.rut or ''
 return True
