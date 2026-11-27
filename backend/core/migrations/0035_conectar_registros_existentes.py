"""Conecta referencias inequívocas sin inventar asignaciones ni datos históricos."""
import uuid
from django.db import migrations
from django.utils import timezone

def connect(apps,schema_editor):
 db=schema_editor.connection.alias
 Registry=apps.get_model('core','RegistroGestion');Activity=apps.get_model('core','Actividad');Attention=apps.get_model('core','Atencion');Commitment=apps.get_model('core','Compromiso');Role=apps.get_model('core','Rol');Policy=apps.get_model('core','PoliticaOperativa')
 def create(obj,kind,description,name,day,**extra):
  return Registry.objects.using(db).create(codigo='GES-'+uuid.uuid4().hex[:20].upper(),delegacion_id=obj.delegacion_id,autor_id=getattr(obj,'autor_id',None) or obj.usuario_id,tipo=kind,descripcion=description,solicitante=name,fecha_solicitud=day,**extra)
 # Detect ambiguous historical merges before touching any row.
 for c in Commitment.objects.using(db).all():
  origins=list(Activity.objects.using(db).filter(compromiso_id=c.pk).values_list('atencion_id',flat=True))
  social=Attention.objects.using(db).filter(compromiso_id=c.pk).exclude(pk__in=[x for x in origins if x])
  if len(origins)>1 or social.count()+(1 if origins else 0)>1:
   raise RuntimeError('Migración detenida: compromiso histórico con varios orígenes; revisar ID '+str(c.pk))
 # A legacy commitment can have several source activities: only a unique origin is merged.
 for a in Activity.objects.using(db).order_by('pk').iterator():
  if a.registro_gestion_id:continue
  r=create(a,'Actividad',a.solicitud,a.contacto,a.fecha,telefono=a.telefono,rut=a.rut_contacto,sector=a.sector,vecino_id=a.vecino_id,territorio_catalogo_id=a.territorio_catalogo_id)
  Activity.objects.using(db).filter(pk=a.pk).update(registro_gestion_id=r.pk)
  if a.atencion_id:Attention.objects.using(db).filter(pk=a.atencion_id,registro_gestion__isnull=True).update(registro_gestion_id=r.pk)
  if a.compromiso_id and Activity.objects.using(db).filter(compromiso_id=a.compromiso_id).count()==1 and not Attention.objects.using(db).filter(compromiso_id=a.compromiso_id).exclude(pk=a.atencion_id).exists():
   Commitment.objects.using(db).filter(pk=a.compromiso_id,registro_gestion__isnull=True).update(registro_gestion_id=r.pk)
 for a in Attention.objects.using(db).filter(registro_gestion__isnull=True).order_by('pk').iterator():
  r=create(a,'Gestión social',a.descripcion,a.solicitante,timezone.localtime(a.fecha_registro).date(),telefono=a.telefono_solicitante,rut=a.rut_solicitante)
  Attention.objects.using(db).filter(pk=a.pk).update(registro_gestion_id=r.pk)
  if a.compromiso_id and not Activity.objects.using(db).filter(compromiso_id=a.compromiso_id).exists() and Attention.objects.using(db).filter(compromiso_id=a.compromiso_id).count()==1:
   Commitment.objects.using(db).filter(pk=a.compromiso_id,registro_gestion__isnull=True).update(registro_gestion_id=r.pk)
 for c in Commitment.objects.using(db).filter(registro_gestion__isnull=True).iterator():
  r=create(c,'Solicitud',c.descripcion,c.solicitante,c.fecha_solicitud,sector=c.sector,vecino_id=c.vecino_id,territorio_catalogo_id=c.territorio_catalogo_id)
  Commitment.objects.using(db).filter(pk=c.pk).update(registro_gestion_id=r.pk)
 # Preserve legacy realised state: an old audited closure remains a closure with its date/result.
 for c in Commitment.objects.using(db).filter(estado='Realizado',cierre_actual__isnull=False).select_related('cierre_actual'):
  Commitment.objects.using(db).filter(pk=c.pk).update(estado='Cerrado',fecha_cierre=c.cierre_actual.fecha,resultado=c.cierre_actual.observacion)
 for role in Role.objects.using(db).all():
  permissions=list(role.permisos or []);manager=role.nombre.strip().casefold() in ('administrador','delegado')
  if manager: permissions+=['asignaciones-metas.'+a for a in ('ver','crear','editar','ver_equipo')]+['cartas.'+a for a in ('ver','crear','editar','gestionar','reasignar','reabrir')]
  elif any(p in permissions for p in ('actividades.ver','compromisos.ver')):permissions+=['asignaciones-metas.ver','cartas.ver']
  if not manager and 'compromisos.crear' in permissions:permissions+=['cartas.crear','cartas.editar']
  role.permisos=list(dict.fromkeys(permissions));role.save(using=db,update_fields=['permisos'])
 # Version policy rather than rewrite the historical policy row.
 old=Policy.objects.using(db).order_by('-version').first()
 if old:
  transitions=dict(old.transiciones);transitions.setdefault('Pendiente',['En proceso','Realizado','Cerrado','No aplica'])
  for state in ('Ingresado','Pendiente','En proceso','Realizado'):
   transitions[state]=list(dict.fromkeys(transitions.get(state,[])+(['Cerrado','No aplica'] if state!='Ingresado' else ['Pendiente','Cerrado','No aplica'])))
  transitions.update({'Cerrado':[],'No aplica':[]})
  Policy.objects.using(db).create(version=old.version+1,transiciones=transitions,motivo='Actualización de estados según requerimientos complementarios: Realizado distingue ejecución de cierre; cierre explícito con resultado.',autor_id=old.autor_id,validada=False,permisos_snapshot=old.permisos_snapshot)

class Migration(migrations.Migration):
 dependencies=[('core','0034_completar_crud_y_fechas')]
 operations=[migrations.RunPython(connect,migrations.RunPython.noop)]
