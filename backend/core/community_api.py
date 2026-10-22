"""Mantenimiento comunitario por delegación activa, permisos y versión."""
import re,uuid
from django.core.exceptions import ValidationError
from django.db import transaction,IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from . import local_api as api,domain_api as domain,neighbors
from .capture_followup import fingerprint
from .models import Vecino,OrganizacionComunitaria as Organizacion,PertenenciaOrganizacion as Pertenencia

ORG_FIELDS=('nombre','tipo','domicilio_legal','territorio','socios_activos','fecha_constitucion','registro_personalidad_juridica','fecha_inscripcion','numero_registro')

def org_data(o):return dict(id=o.pk,version=o.version,activo=o.activo,delegacion=o.delegacion_id,**{f:getattr(o,f) for f in ORG_FIELDS})
def membership_data(p):return dict(id=p.pk,version=p.version,activo=p.activo,vecino=p.vecino_id,vecino_nombre=p.vecino.nombre,vecino_activo=p.vecino.activo,organizacion=p.organizacion_id,organizacion_nombre=p.organizacion.nombre,organizacion_activa=p.organizacion.activo,rol=p.rol)
def neighbor_data(o):
 d=neighbors.representation(o);d['pertenencias']=[membership_data(p) for p in o.pertenencias.select_related('vecino','organizacion')];return d

def response(data=None,**extra):
 r=api.ok(data,**extra);r['Cache-Control']='private, no-store';return r

def scoped(request,resource):
 d=api.active_delegation(request)
 if resource=='vecinos':return Vecino.objects.filter(delegacion=d)
 if resource=='organizaciones':return Organizacion.objects.filter(delegacion=d)
 return Pertenencia.objects.filter(vecino__delegacion=d,organizacion__delegacion=d).select_related('vecino','organizacion')

def serialize(resource,obj):return {'vecinos':neighbor_data,'organizaciones':org_data,'pertenencias':membership_data}[resource](obj)

def fields(obj,data,allowed):
 for f,v in data.items():
  if f not in allowed:raise ValidationError('Campo no editable: '+f)
  if f=='socios_activos':
   if v in ['',None]:v=None
   elif isinstance(v,bool) or not str(v).isdigit():raise ValidationError('Socios activos debe ser un entero no negativo.')
   else:v=int(v)
  elif f in ['fecha_constitucion','fecha_inscripcion']:
   if v in ['',None]:v=None
   elif not isinstance(v,str):raise ValidationError('Fecha inválida.')
  else:
   if not isinstance(v,str):raise ValidationError('Los datos deben ser texto.')
   v=v.strip()
   if f in ['nombre','territorio','tipo'] and not v:raise ValidationError(f+': campo obligatorio.')
   if f=='nombre':v=' '.join(v.split())
   if f=='rut':v=neighbors.normalize_rut(v) or None
   if f=='telefono' and v and not re.fullmatch(r'\+?[0-9 ()-]{8,20}',v):raise ValidationError('Teléfono inválido.')
  setattr(obj,f,v)
 obj.full_clean()

def replay_org(request,key,digest):
 obj=Organizacion.objects.filter(clave_idempotencia=key).first()
 if obj is None:return None
 if obj.delegacion_id!=api.active_delegation(request).pk or obj.creado_por_id!=request.user.pk or obj.captura_hash!=digest:return api.error('La clave pertenece a otro registro.',409)
 return response(org_data(obj),is_duplicate_prevented=True)

@require_http_methods(['GET','POST','PATCH'])
def resource(request,resource,pk=None,action=None):
 verb='desactivar' if action=='estado' else 'ver' if request.method=='GET' else 'crear' if request.method=='POST' and pk is None else 'editar'
 denied=domain.gate(request,resource,verb)
 if denied:return denied
 if action and request.method!='POST':return api.error('Método no permitido.',405)
 if pk and request.method=='POST' and not action:return api.error('Método no permitido.',405)
 if not pk and request.method=='PATCH':return api.error('Selecciona un registro.',405)
 try:
  if request.method=='GET':
   if pk:
    obj=scoped(request,resource).filter(pk=pk).first()
    return response(serialize(resource,obj)) if obj else api.error('Registro no encontrado.',404)
   qs=scoped(request,resource);state=request.GET.get('estado','activos')
   if state in ['activos','inactivos']:qs=qs.filter(activo=state=='activos')
   query=request.GET.get('q','').strip()[:100]
   if query:
    qs=qs.filter(Q(nombre__icontains=query)|Q(rut__icontains=query)) if resource=='vecinos' else qs.filter(nombre__icontains=query) if resource=='organizaciones' else qs.filter(Q(vecino__nombre__icontains=query)|Q(organizacion__nombre__icontains=query))
   for f in ['vecino','organizacion']:
    if resource=='pertenencias' and request.GET.get(f):
     if not request.GET[f].isdigit():raise ValidationError('Referencia inválida.')
     qs=qs.filter(**{f+'_id':request.GET[f]})
   page=Paginator(qs,20).get_page(request.GET.get('page',1));return response(results=[serialize(resource,o) for o in page],count=page.paginator.count,total_pages=page.paginator.num_pages,page=page.number)
  data=api.body(request)
  with transaction.atomic():
   obj=scoped(request,resource).select_for_update().filter(pk=pk).first() if pk else None
   if pk and obj is None:return api.error('Registro no encontrado.',404)
   before=serialize(resource,obj) if obj else None
   if obj:
    if isinstance(data.get('_version'),bool) or data.get('_version')!=obj.version:return api.error('El registro cambió. Actualiza el listado antes de guardar.',409)
    data.pop('_version')
   if action=='estado':
    if set(data)-{'activo','motivo'} or not isinstance(data.get('activo'),bool) or not isinstance(data.get('motivo'),str) or not data['motivo'].strip() or len(data['motivo'])>2000:raise ValidationError('Indica estado y motivo obligatorio de hasta 2000 caracteres.')
    if resource=='pertenencias' and data['activo'] and (not obj.vecino.activo or not obj.organizacion.activo):raise ValidationError('No puedes activar un vínculo con vecino u organización inactivos.')
    obj.activo=data['activo'];obj.version+=1;obj.save();after=serialize(resource,obj);after['motivo']=data['motivo'].strip();api.record_event(request,resource,obj.pk,'activar' if obj.activo else 'desactivar',before,after);return response(serialize(resource,obj))
   if obj and not obj.activo:raise ValidationError('Reactiva el registro antes de editarlo.')
   if resource=='vecinos':
    if not obj:raise ValidationError('Usa el formulario de registro de vecinos.')
    fields(obj,data,neighbors.EDIT_FIELDS)
   elif resource=='organizaciones':
    if obj:fields(obj,data,ORG_FIELDS)
    else:
     key=data.pop('clave_idempotencia',None)
     if not isinstance(key,str) or not key.strip() or len(key)>64:raise ValidationError('Falta clave de registro.')
     digest=fingerprint(data);prior=replay_org(request,key,digest)
     if prior:return prior
     obj=Organizacion(delegacion=api.active_delegation(request),creado_por=request.user,clave_idempotencia=key,captura_hash=digest);fields(obj,data,ORG_FIELDS)
   else:
    if obj:
     if not obj.vecino.activo or not obj.organizacion.activo:raise ValidationError('No puedes cambiar una pertenencia con vecino u organización inactivos.')
     fields(obj,data,('rol',))
    else:
     if set(data)-{'vecino','organizacion','rol'}:raise ValidationError('Hay campos no editables.')
     ids=[data.get('vecino'),data.get('organizacion')]
     if any(isinstance(v,bool) or not str(v).isdigit() for v in ids):raise ValidationError('Selecciona vecino y organización.')
     v=scoped(request,'vecinos').select_for_update().filter(pk=ids[0]).first();o=scoped(request,'organizaciones').select_for_update().filter(pk=ids[1]).first()
     if v is None or o is None:return api.error('Vecino u organización no encontrados.',404)
     if not v.activo or not o.activo:raise ValidationError('Vecino y organización deben estar activos.')
     if Pertenencia.objects.filter(vecino=v,organizacion=o).exists():return api.error('La pertenencia ya existe. Consúltala o reactívala.',409)
     obj=Pertenencia(vecino=v,organizacion=o,rol=data.get('rol',''),creado_por=request.user);obj.full_clean()
   if pk:obj.version+=1
   obj.save();api.record_event(request,resource,obj.pk,'editar' if pk else 'crear',before,serialize(resource,obj));r=response(serialize(resource,obj));r.status_code=200 if pk else 201;return r
 except IntegrityError:
  if resource=='organizaciones' and 'key' in locals():
   prior=replay_org(request,key,digest)
   if prior:return prior
  return api.error('El registro ya existe o cambió simultáneamente. Actualiza el listado.',409)
 except ValidationError as ex:
  if resource=='organizaciones' and 'key' in locals() and 'digest' in locals():
   prior=replay_org(request,key,digest)
   if prior:return prior
  return api.error('; '.join(ex.messages))
 except (TypeError,ValueError):return api.error('Datos inválidos.')
