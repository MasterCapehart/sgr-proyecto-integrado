"""Los permisos accidentales no habilitan funciones reservadas al gestor."""
import uuid
from django.test import TestCase
from . import test_milestones as milestones
from .models import Rol, Hito, ReglaActividad

PERMISSIONS = ['hitos.' + a for a in ['ver','ver_equipo','crear','editar','asignar','avanzar']] + ['clasificacion-actividades.ver','clasificacion-actividades.configurar']

class ReservedManagementTests(TestCase):
 setUp = milestones.MilestoneTests.setUp
 payload = milestones.MilestoneTests.payload
 hito = milestones.MilestoneTests.hito
 task = milestones.MilestoneTests.task
 send = milestones.MilestoneTests.send
 def profile(self, name, permissions=None):
  self.u.is_superuser = False
  self.u.rol = Rol.objects.create(nombre=name, permisos=PERMISSIONS if permissions is None else permissions)
  self.u.save()
  self.client.force_login(self.u)
 def publish(self):
  return self.send(f'/api/clasificacion-actividades/{self.i.pk}/',dict(_version=0,clasificacion='Coordinación',valida_para_puntuar=False,motivo='Prueba de perfil',clave_idempotencia=uuid.uuid4().hex))
 def test_other_roles_cannot_manage_even_with_permissions(self):
  h = self.hito(); t = self.task(h)
  for name in ['Coordinador','Funcionario','Verificador','Consulta','Delegado suplente']:
   with self.subTest(role=name):
    self.profile(name)
    for url, data, method in [('/api/hitos/',self.payload(),'post'),(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],nombre='Cambio'),'patch'),(f'/api/hitos/{h["id"]}/tareas/',dict(nombre='Nueva'),'post'),(f'/api/hitos/tareas/{t["id"]}/',dict(_version=t['version'],nombre='Cambio'),'patch'),(f'/api/hitos/tareas/{t["id"]}/tubo/',dict(_version=t['version']),'post')]:
     self.assertEqual(self.send(url,data,method).status_code,403,url)
    listing=self.client.get('/api/hitos/').json()
    self.assertFalse(listing['puede_crear'])
    detail=self.client.get(f'/api/hitos/{h["id"]}/').json()['data']
    self.assertFalse(detail['puede_editar']); self.assertFalse(detail['puede_asignar'])
    self.assertTrue(detail['puede_avanzar'])
    self.assertEqual(self.client.get('/api/hitos/opciones/').json()['responsables'],[])
    self.assertFalse(self.client.get('/api/clasificacion-actividades/').json()['puede_configurar'])
    self.assertEqual(self.publish().status_code,403)
  self.assertEqual(Hito.objects.count(),1); self.assertFalse(ReglaActividad.objects.exists())
 def test_canonical_managers_keep_create_edit_assign_and_publish(self):
  for name in ['Administrador',' Delegado ']:
   with self.subTest(role=name):
    self.profile(name)
    h=self.hito(); t=self.task(h)
    self.assertEqual(self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],nombre='Editado'),'patch').status_code,200)
    self.assertEqual(self.send(f'/api/hitos/tareas/{t["id"]}/',dict(_version=t['version'],nombre='Editada'),'patch').status_code,200)
    self.assertTrue(self.client.get('/api/hitos/').json()['puede_crear'])
    self.assertTrue(self.client.get('/api/clasificacion-actividades/').json()['puede_configurar'])
    # Un ítem nuevo evita que la versión anterior interfiera con la autorización.
    ReglaActividad.objects.all().delete()
    self.assertEqual(self.publish().status_code,201)
 def test_manager_still_needs_permissions(self):
  self.profile('Delegado', ['hitos.ver','clasificacion-actividades.ver'])
  self.assertEqual(self.send('/api/hitos/',self.payload()).status_code,403)
  self.assertEqual(self.publish().status_code,403)
 def test_inactive_manager_role_denied(self):
  self.profile('Administrador'); self.u.rol.estado=False; self.u.rol.save()
  self.assertEqual(self.send('/api/hitos/',self.payload()).status_code,403)
  self.assertEqual(self.publish().status_code,403)
