"""Fuente común de gestión y estado de seguimiento, con compatibilidad histórica."""
from django.core.exceptions import ValidationError,PermissionDenied
from django.utils import timezone
from django.db.models import F
from .models import RegistroGestion,Actividad,Atencion,Compromiso
TERMINAL=('Cerrado','No aplica')

def shared_values(source):
 if isinstance(source,Actividad):
  return dict(descripcion=source.solicitud,solicitante=source.contacto,fecha_solicitud=source.fecha,telefono=source.telefono,rut=source.rut_contacto,sector=source.sector,vecino_id=source.vecino_id,territorio_catalogo_id=source.territorio_catalogo_id)
 if isinstance(source,Atencion):
  return dict(descripcion=source.descripcion,solicitante=source.solicitante,fecha_solicitud=source.fecha_registro.date() if source.fecha_registro else timezone.localdate(),telefono=source.telefono_solicitante,rut=source.rut_solicitante,sector='',vecino_id=None,territorio_catalogo_id=None)
 return dict(descripcion=source.descripcion,solicitante=source.solicitante,fecha_solicitud=source.fecha_solicitud,telefono=(source.vecino.telefono if source.vecino_id else ''),rut=(source.vecino.rut or '' if source.vecino_id else ''),sector=source.sector,vecino_id=source.vecino_id,territorio_catalogo_id=source.territorio_catalogo_id)

def validate_link(request,source,commitment):
 from . import local_api as api
 if not api.allowed(request.user,'compromisos','editar'):raise PermissionDenied('No tienes permiso para vincular este seguimiento.')
 manager=request.user.is_superuser or bool(request.user.rol_id and request.user.rol.estado and request.user.rol.nombre.strip().casefold() in ['administrador','delegado'] and api.allowed(request.user,'compromisos','editar_equipo'))
 if commitment.responsable_id!=request.user.pk and not manager:raise PermissionDenied('Solo el responsable o gestor autorizado puede vincular este seguimiento.')
 if commitment.estado in TERMINAL:raise ValidationError('Reabre el seguimiento antes de vincular un origen.')
 activities=Actividad.objects.filter(compromiso=commitment)
 attentions=Atencion.objects.filter(compromiso=commitment)
 if isinstance(source,Actividad):
  activities=activities.exclude(pk=source.pk)
  if source.atencion_id:attentions=attentions.exclude(pk=source.atencion_id)
 else:attentions=attentions.exclude(pk=source.pk)
 if activities.exists() or attentions.exists():raise ValidationError('El seguimiento ya tiene un registro de origen.')
 if source.registro_gestion_id and commitment.registro_gestion_id and source.registro_gestion_id!=commitment.registro_gestion_id:raise ValidationError('El registro y el seguimiento ya tienen cabeceras diferentes; no se pueden fusionar implícitamente.')
 if commitment.registro_gestion_id:source.registro_gestion=commitment.registro_gestion

def sync_source(source):
 """Actualiza una sola cabecera y sus instantáneas de compatibilidad."""
 values=shared_values(source)
 if not source.registro_gestion_id:
  registry=RegistroGestion.objects.create(delegacion=source.delegacion,autor=source.autor if hasattr(source,'autor') else source.usuario,tipo='Actividad' if isinstance(source,Actividad) else 'Gestión social' if isinstance(source,Atencion) else 'Solicitud',**values)
  type(source).objects.filter(pk=source.pk).update(registro_gestion=registry);source.registro_gestion=registry
 else:
  registry=RegistroGestion.objects.select_for_update().get(pk=source.registro_gestion_id)
  for key,value in values.items():setattr(registry,key,value)
  registry.version+=1;registry.save()
 if isinstance(source,Actividad):
  if source.atencion_id:Atencion.objects.filter(pk=source.atencion_id).update(registro_gestion=registry,descripcion=source.solicitud,solicitante=source.contacto,telefono_solicitante=source.telefono,rut_solicitante=source.rut_contacto,gestion_realizada=source.accion)
  if source.compromiso_id:
   Compromiso.objects.filter(pk=source.compromiso_id).update(registro_gestion=registry,version=F('version')+1,fecha_solicitud=registry.fecha_solicitud,descripcion=registry.descripcion,solicitante=registry.solicitante,sector=registry.sector,vecino_id=registry.vecino_id,territorio_catalogo_id=registry.territorio_catalogo_id)
 elif isinstance(source,Atencion) and source.compromiso_id:
  Compromiso.objects.filter(pk=source.compromiso_id).update(registro_gestion=registry,version=F('version')+1,fecha_solicitud=registry.fecha_solicitud,descripcion=registry.descripcion,solicitante=registry.solicitante)
 return registry

def ensure_commitment(obj,source=None):
 if source is not None:
  registry=sync_source(source)
  if not obj.registro_gestion_id:
   obj.registro_gestion=registry;obj.save(update_fields=['registro_gestion'])
  return registry
 if obj.registro_gestion_id:
  registry=obj.registro_gestion
  # Bound activity/social is canonical. Direct requests own their header.
  if not Actividad.objects.filter(registro_gestion=registry).exists() and not Atencion.objects.filter(registro_gestion=registry).exists():return sync_source(obj)
  return registry
 return sync_source(obj)

def validate_shared_edit(obj,data):
 if not obj.registro_gestion_id:return
 registry=obj.registro_gestion
 bound=Actividad.objects.filter(registro_gestion=registry).exists() or Atencion.objects.filter(registro_gestion=registry).exists()
 if not bound:return
 fields={'descripcion':'descripcion','solicitante':'solicitante','sector':'sector','fecha_solicitud':'fecha_solicitud','vecino':'vecino_id','territorio_catalogo':'territorio_catalogo_id'}
 for field,attr in fields.items():
  if field in data and str(data[field] or '')!=str(getattr(registry,attr) or ''):raise ValidationError('Los datos comunes provienen del registro de origen. Corrígelos desde su ficha; aquí modifica el seguimiento.')

def representation(obj,result):
 result['registro_gestion']=obj.registro_gestion_id
 if isinstance(obj,Compromiso):
  result['resultado']=obj.resultado;result['fecha_cierre']=obj.fecha_cierre.isoformat() if obj.fecha_cierre else None
  result['datos_desde_origen']=bool(obj.registro_gestion_id and (Actividad.objects.filter(registro_gestion_id=obj.registro_gestion_id).exists() or Atencion.objects.filter(registro_gestion_id=obj.registro_gestion_id).exists()))
  result['vencido']=obj.fecha_comprometida<timezone.localdate() and obj.estado not in TERMINAL
 if obj.registro_gestion_id:
  r=obj.registro_gestion;result['codigo_gestion']=r.codigo
  if isinstance(obj,Compromiso):result.update(descripcion=r.descripcion,solicitante=r.solicitante,fecha_solicitud=r.fecha_solicitud,sector=r.sector,vecino=r.vecino_id,territorio_catalogo=r.territorio_catalogo_id,telefono=r.telefono,rut_contacto=r.rut)
 return result
