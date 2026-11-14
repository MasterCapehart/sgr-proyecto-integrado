from django.db import migrations

def grant(apps,schema_editor):
 Rol=apps.get_model('core','Rol')
 for rol in Rol.objects.using(schema_editor.connection.alias).all():
  if any(p in (rol.permisos or []) for p in ['vecinos.ver','vecinos.crear','organizaciones.ver','actividades.crear','hitos.ver']):
   rol.permisos=list(dict.fromkeys(list(rol.permisos or [])+['territorios.ver']))
   rol.save(using=schema_editor.connection.alias,update_fields=['permisos'])
  if rol.nombre.strip().casefold() in ('administrador','delegado'):
   rol.permisos=list(dict.fromkeys(list(rol.permisos or [])+['territorios.'+a for a in ('ver','crear','editar','desactivar')]))
   rol.save(using=schema_editor.connection.alias,update_fields=['permisos'])

class Migration(migrations.Migration):
 dependencies=[('core','0030_territorios_catalogo')]
 operations=[migrations.RunPython(grant,migrations.RunPython.noop)]
