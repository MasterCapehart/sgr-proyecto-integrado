from django.test import TestCase
from .models import Cargo, Usuario, ItemMeta, PeriodoGestion, ConfiguracionMeta
from .absences import meta_rows

class CargoMetaTests(TestCase):
 def setUp(self):
  self.a=Cargo.objects.create(codigo='MC-A',nombre='Territorial 1')
  self.b=Cargo.objects.create(codigo='MC-B',nombre='Territorial 3')
  self.u=Usuario.objects.create_user('mc-worker',cargo=self.a)
  self.p=PeriodoGestion.objects.create(codigo='MC26',nombre='Prueba cargo',fecha_inicio='2026-07-01',fecha_fin='2026-09-30')
  self.i=ItemMeta.objects.create(codigo='MC-ORG',nombre='Conformación de organizaciones')
 def meta(self,cargo=None,**kw):
  return ConfiguracionMeta.objects.create(item=self.i,periodo=self.p.codigo,periodo_gestion=self.p,cargo=cargo,**kw)
 def test_specific_overrides_general_without_duplicate(self):
  self.meta(meta_esperada=3)
  specific=self.meta(self.a,meta_esperada=1)
  self.meta(self.b,meta_esperada=10)
  self.assertEqual(list(meta_rows(self.u,self.p)),[specific])
 def test_general_fallback_and_no_cross_cargo(self):
  general=self.meta(meta_esperada=3);self.meta(self.b,meta_esperada=10)
  self.assertEqual(list(meta_rows(self.u,self.p)),[general])
  self.u.cargo=None;self.u.save()
  self.assertEqual(list(meta_rows(self.u,self.p)),[general])
 def test_inactive_specific_does_not_hide_general(self):
  general=self.meta();self.meta(self.a,estado=False)
  self.assertEqual(list(meta_rows(self.u,self.p)),[general])
 def test_different_targets_and_weights_survive_selection(self):
  a=self.meta(self.a,meta_esperada=1,ponderacion=15)
  b=self.meta(self.b,meta_esperada=10,ponderacion=25)
  self.assertEqual(list(meta_rows(self.u,self.p)),[a])
  self.u.cargo=self.b;self.u.save()
  self.assertEqual(list(meta_rows(self.u,self.p)),[b])
 def test_database_rejects_duplicates_including_general(self):
  from django.db import IntegrityError,transaction
  for cargo in [None,self.a]:
   self.meta(cargo)
   with self.assertRaises(IntegrityError),transaction.atomic():self.meta(cargo)
 def test_api_cargo_scope_and_closed_period(self):
  admin=Usuario.objects.create_superuser('mc-admin','mc@example.test','LocalTest!234')
  self.client.force_login(admin)
  payload=dict(item=self.i.pk,periodo_gestion=self.p.pk,meta_esperada=1,ponderacion=25,cargo=self.a.pk)
  response=self.client.post('/api/configuraciones-metas/',payload,content_type='application/json')
  self.assertEqual(response.status_code,201,response.content)
  self.assertEqual(response.json()['data']['cargo'],self.a.pk)
  self.assertEqual(self.client.post('/api/configuraciones-metas/',payload,content_type='application/json').status_code,400)
  payload['cargo']=self.b.pk;payload['meta_esperada']=10
  response=self.client.post('/api/configuraciones-metas/',payload,content_type='application/json')
  self.assertEqual(response.status_code,201,response.content)
  self.p.cerrado=True;self.p.save();payload['cargo']=None
  self.assertEqual(self.client.post('/api/configuraciones-metas/',payload,content_type='application/json').status_code,400)

from . import test_absences as absence_fixtures
class CargoCalendarTests(TestCase):
 setUp=absence_fixtures.AbsenceTests.setUp
 calendar=absence_fixtures.AbsenceTests.calendar
 absence=absence_fixtures.AbsenceTests.absence
 summary=absence_fixtures.AbsenceTests.summary
 send=absence_fixtures.AbsenceTests.send
 def test_existing_calendar_keeps_item_proration_after_specific_target(self):
  cal=self.calendar();self.absence(cal)
  cargo=Cargo.objects.create(codigo='MC-C',nombre='Gestor específico');self.worker.cargo=cargo;self.worker.save()
  specific=ConfiguracionMeta.objects.create(item=self.i,periodo_gestion=self.p,periodo=self.p.codigo,cargo=cargo,meta_esperada=40,ponderacion=25)
  row=self.summary()['metas'][0]
  self.assertEqual(row['id'],specific.pk);self.assertTrue(row['prorrateable']);self.assertEqual(row['meta_ajustada'],'30.00')
 def test_closure_preserves_specific_scope_after_cargo_change(self):
  cargo=Cargo.objects.create(codigo='MC-S',nombre='Cargo al cierre');self.worker.cargo=cargo;self.worker.save()
  specific=ConfiguracionMeta.objects.create(item=self.i,periodo_gestion=self.p,periodo=self.p.codigo,cargo=cargo,meta_esperada=40,ponderacion=25)
  self.calendar(metas_prorrateables=[specific.pk])
  response=self.send(f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Cierre de prueba'))
  self.assertEqual(response.status_code,200,response.content)
  before=self.summary();self.worker.cargo=None;self.worker.save();specific.meta_esperada=99;specific.save()
  self.assertEqual(self.summary(),before)
  self.assertEqual(before['metas'][0]['cargo_meta'],cargo.pk)
 def test_collective_sums_specific_targets_without_duplicate_general(self):
  from .models import CalendarioFuncionario
  a=Cargo.objects.create(codigo='MC-CA',nombre='Cargo equipo A');b=Cargo.objects.create(codigo='MC-CB',nombre='Cargo equipo B')
  self.worker.cargo=a;self.worker.save()
  ma=ConfiguracionMeta.objects.create(item=self.i,periodo_gestion=self.p,periodo=self.p.codigo,cargo=a,meta_esperada=40,ponderacion=25)
  mb=ConfiguracionMeta.objects.create(item=self.i,periodo_gestion=self.p,periodo=self.p.codigo,cargo=b,meta_esperada=10,ponderacion=20)
  self.calendar(metas_prorrateables=[ma.pk])
  second=Usuario.objects.create_user('mc-second',rol=self.worker.rol,delegacion=self.d,cargo=b)
  self.calendar(funcionario=second.pk,metas_prorrateables=[mb.pk])
  response=self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk})
  self.assertEqual(response.status_code,200,response.content)
  data=response.json()['data'];self.assertEqual(data['items'][0]['meta'],'50.00')
  self.assertFalse(data['pesos_compatibles']);self.assertIsNone(data['cumplimiento'])
