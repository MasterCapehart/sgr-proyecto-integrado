"""Asignaciones individuales visibles al funcionario sin acceso administrativo."""
from datetime import date
from django.test import TestCase
from . import test_capture_form as capture_tests
from .models import Rol, Cargo, ItemMeta, PeriodoGestion, Actividad
from .goal_models import AsignacionMeta


class CaptureAssignmentTests(TestCase):
 setUp=capture_tests.CaptureFormTests.setUp
 activity=capture_tests.CaptureFormTests.activity
 payload=capture_tests.CaptureFormTests.payload
 post=capture_tests.CaptureFormTests.post

 def prepare(self):
  self.u.is_superuser=False
  self.u.rol=Rol.objects.create(nombre='Funcionario captura metas',permisos=['actividades.crear','actividades.ver'])
  self.u.cargo=Cargo.objects.create(codigo='CAPMETA',nombre='Cargo funcionario QA')
  self.u.save()
  other_cargo=Cargo.objects.create(codigo='OTROMETA',nombre='Cargo diferente')
  item=ItemMeta.objects.create(codigo='ASIGNEXPL',nombre='Meta asignada explícitamente')
  item.cargos.add(other_cargo)
  period=PeriodoGestion.objects.create(codigo='Q326META',nombre='Julio–septiembre 2026',anio=2026,numero=3,fecha_inicio=date(2026,7,1),fecha_fin=date(2026,9,30))
  assignment=AsignacionMeta.objects.create(funcionario=self.u,item=item,periodo=period,delegacion=self.d,autor=self.u,cantidad_objetivo=100,ponderacion=50)
  return item,period,assignment

 def test_own_assigned_goal_visible_without_administration_permission(self):
  item,period,a=self.prepare()
  r=self.client.get('/api/captura/opciones/?fecha=2026-08-15');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual([x['id'] for x in r.json()['asignaciones']],[a.pk])
  self.assertIn(item.pk,[x['id'] for x in r.json()['items']])
  self.assertEqual(self.client.get('/api/asignaciones-metas/').status_code,403)

 def test_explicit_assignment_authorizes_only_its_own_item_and_creates_draft(self):
  item,period,a=self.prepare()
  data=self.payload();data['actividad'].update(fecha='2026-08-15',item=item.pk,asignacion_meta=a.pk)
  r=self.post(data);self.assertEqual(r.status_code,201,r.content)
  activity=Actividad.objects.get();self.assertEqual(activity.asignacion_meta_id,a.pk);self.assertEqual(activity.estado,'Borrador')
  data=self.payload();data['actividad'].update(fecha='2026-08-15',item=item.pk)
  self.assertEqual(self.post(data).status_code,400)

 def test_out_of_quarter_or_foreign_or_inactive_assignment_not_offered(self):
  item,period,a=self.prepare()
  foreign=AsignacionMeta.objects.create(funcionario=self.other,item=item,periodo=period,delegacion=self.other_d,autor=self.u,cantidad_objetivo=20,ponderacion=10)
  r=self.client.get('/api/captura/opciones/?fecha=2026-10-15');self.assertEqual(r.json()['asignaciones'],[])
  self.assertNotIn(item.pk,[x['id'] for x in r.json()['items']])
  r=self.client.get('/api/captura/opciones/?fecha=2026-08-15');self.assertNotIn(foreign.pk,[x['id'] for x in r.json()['asignaciones']])
  a.estado=False;a.save();self.assertEqual(self.client.get('/api/captura/opciones/?fecha=2026-08-15').json()['asignaciones'],[])
  data=self.payload();data['actividad'].update(fecha='2026-08-15',item=item.pk,asignacion_meta=foreign.pk)
  self.assertEqual(self.post(data).status_code,400)

 def test_invalid_date_is_rejected(self):
  self.prepare();self.assertEqual(self.client.get('/api/captura/opciones/?fecha=no-es-fecha').status_code,400)
