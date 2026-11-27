"""Catálogo territorial limitado por delegación y permisos explícitos."""
from django.core.exceptions import ValidationError
from django.db import transaction,IntegrityError
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from . import local_api as api,domain_api as domain
from .models import Territorio

def representation(o):
 return dict(id=o.pk,codigo=o.codigo,nombre=o.nombre,descripcion=o.descripcion,delegacion=o.delegacion_id,delegacion_nombre=o.delegacion.nombre,activo=o.activo,version=o.version)

def bind(obj,value):
 if value in (None,''):
  obj.territorio_catalogo=None
  return
 if isinstance(value,bool) or not str(value).isdigit():raise ValidationError('Selecciona un territorio válido.')
 t=Territorio.objects.filter(pk=value,delegacion_id=obj.delegacion_id).first()
 if t is None:raise ValidationError('El territorio no pertenece a la delegación del registro.')
 if not t.activo and (not obj.pk or obj.territorio_catalogo_id!=t.pk):raise ValidationError('El territorio está inactivo. Selecciona uno activo.')
 obj.territorio_catalogo=t

@require_http_methods(['GET','POST','PATCH'])
def records(request,pk=None,action=None):
 verb='desactivar' if action=='estado' else 'ver' if request.method=='GET' else 'crear' if not pk else 'editar'
 denied=domain.gate(request,'territorios',verb)
 if denied:return denied
 if (action and request.method!='POST') or (pk and request.method=='POST' and not action) or (not pk and request.method=='PATCH'):return api.error('Método no permitido.',405)
 d=api.active_delegation(request)
 qs=Territorio.objects.filter(delegacion=d).select_related('delegacion')
 try:
  if request.method=='GET':
   if pk:
    obj=qs.filter(pk=pk).first()
    return api.ok(representation(obj)) if obj else api.error('Territorio no encontrado.',404)
   estado=request.GET.get('estado','activos')
   if estado not in ('activos','inactivos','todos'):raise ValidationError('Estado inválido.')
   if estado!='todos':qs=qs.filter(activo=estado=='activos')
   q=request.GET.get('q','').strip()[:100]
   if q:qs=qs.filter(Q(nombre__icontains=q)|Q(codigo__icontains=q))
   page=Paginator(qs,20).get_page(request.GET.get('page',1))
   return api.ok(results=[representation(o) for o in page],count=page.paginator.count,total_pages=page.paginator.num_pages,page=page.number,delegacion=dict(id=d.pk,nombre=d.nombre))
  data=api.body(request)
  with transaction.atomic():
   obj=qs.select_for_update().filter(pk=pk).first() if pk else Territorio(delegacion=d)
   if obj is None:return api.error('Territorio no encontrado.',404)
   before=representation(obj) if pk else None
   if pk:
    version=data.pop('_version',None)
    if isinstance(version,bool) or version!=obj.version:return api.error('El territorio cambió. Actualiza el listado.',409)
   if action:
    if set(data)-{'activo','motivo'} or not isinstance(data.get('activo'),bool) or not isinstance(data.get('motivo'),str) or not data['motivo'].strip() or len(data['motivo'])>2000:raise ValidationError('Indica el estado y un motivo válido.')
    obj.activo=data['activo']
   else:
    if set(data)-{'nombre','descripcion'}:raise ValidationError('Solo puedes modificar nombre y descripción.')
    if pk and not obj.activo:raise ValidationError('Reactiva el territorio antes de editarlo.')
    for field in ['nombre','descripcion']:
     if field in data:
      if not isinstance(data[field],str):raise ValidationError('Nombre y descripción deben ser texto.')
      setattr(obj,field,data[field].strip())
   obj.clean()
   if Territorio.objects.filter(delegacion=d,nombre_normalizado=obj.nombre_normalizado).exclude(pk=obj.pk).exists():return api.error('Ya existe un territorio con ese nombre en esta delegación.',409)
   obj.full_clean()
   if pk:obj.version+=1
   obj.save()
   after=representation(obj)
   if action:after['motivo']=data['motivo'].strip()
   api.record_event(request,'territorios',obj.pk,'estado' if action else 'editar' if pk else 'crear',before,after)
   response=api.ok(representation(obj));response.status_code=200 if pk else 201
   return response
 except ValidationError as ex:return api.error('; '.join(ex.messages))
 except IntegrityError:return api.error('El territorio ya existe o fue modificado por otra solicitud.',409)
