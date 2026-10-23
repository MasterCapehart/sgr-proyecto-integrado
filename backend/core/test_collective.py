from decimal import Decimal
from django.test import TestCase
from . import test_performance as fixtures
from .models import Usuario,Delegacion,CalendarioFuncionario,Cargo

class CollectiveTests(TestCase):
 setUp=fixtures.PerformanceTests.setUp
 send=fixtures.PerformanceTests.send
 calendar=fixtures.PerformanceTests.calendar
 activity=fixtures.PerformanceTests.activity
 def result(self,**params):
  r=self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}|params);self.assertEqual(r.status_code,200,r.content);return r.json()['data']
 def second(self):
  user=Usuario.objects.create_user('segundo',rol=self.worker.rol,delegacion=self.d)
  self.calendar(funcionario=user.pk);return user
 def test_suma_aportes_limitados_no_compensa_exceso(self):
  self.second()
  for _ in range(13):self.activity()
  r=self.result();row=r['items'][0]
  self.assertEqual(row['meta'],'20.00');self.assertEqual(row['reconocido'],'12.00');self.assertEqual(row['cumplimiento'],'60.00');self.assertEqual(row['exceso'],'1.00');self.assertEqual(r['cumplimiento'],'60.00');self.assertEqual(row['validas'],13)
 def test_metas_ajustadas_distintas_no_promedia_porcentajes(self):
  second=self.second();cal=CalendarioFuncionario.objects.get(funcionario=second,periodo=self.p);cal.semana=['Mañana']*5+['No laboral']*2;cal.save()
  # La meta se ajusta por ausencia, no por longitud de jornada.
  from .models import AusenciaFuncionario
  AusenciaFuncionario.objects.create(calendario=cal,delegacion=self.d,autor=self.u,tipo='Vacaciones',inicio='2026-02-02',fin='2026-02-13',jornada='Mañana',justificacion='QA')
  for _ in range(10):self.activity()
  row=self.result()['items'][0];self.assertEqual(row['meta'],'15.00');self.assertEqual(row['cumplimiento'],'66.67')
 def test_sin_calendario_cobertura_no_falso_cero(self):
  second=Usuario.objects.create_user('sin_cal',rol=self.worker.rol,delegacion=self.d)
  r=self.result();self.assertGreater(r['sin_evaluacion'],0);self.assertEqual(r['evaluados'],1);self.assertIsNone(next(p for p in r['personas'] if p['id']==second.pk)['cumplimiento'])
 def test_permisos_rol_y_delegacion(self):
  self.client.force_login(self.worker);self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).status_code,403)
  self.client.force_login(self.u);self.role.permisos.remove('ausencias.ver_equipo');self.role.save();self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).status_code,403)
  self.role.permisos.append('ausencias.ver_equipo');self.role.save();other=Delegacion.objects.create(codigo='COL2',nombre='Ajena');Usuario.objects.create_user('ajeno',delegacion=other);self.assertNotIn('ajeno',str(self.result()))
 def test_cierre_no_reconstruye_equipo_actual(self):
  self.activity();self.send(f'/api/periodos/{self.p.pk}/cerrar/',{'_version':self.p.version,'motivo':'Cierre'})
  before=self.result();self.worker.is_active=False;self.worker.delegacion=None;self.worker.save();self.m.meta_esperada=999;self.m.save();self.assertEqual(self.result(),before);self.assertTrue(before['cerrado'])
 def test_area_y_territorio_sin_datos_sensibles(self):
  cargo=Cargo.objects.create(codigo='COL',nombre='Cargo colectivo',area='Territorial');self.worker.cargo=cargo;self.worker.save();self.activity(sector='San Juan');self.activity(sector='san juan');self.activity(sector='')
  r=self.result(area='Territorial');self.assertEqual(len(r['personas']),1);self.assertEqual(r['territorios'][0]['registradas'],2);self.assertNotIn('912345678',str(r));self.assertNotIn('Persona ficticia',str(r))
 def test_sin_datos_e_identificadores_invalidos(self):
  self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':'abc'}).status_code,400)
  self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk,'delegacion':999}).status_code,400)
  r=self.result(area='No existe');self.assertEqual(r['personas'],[]);self.assertIsNone(r['cumplimiento'])
 def test_anonimo_y_otros_roles_no_ven_equipo(self):
  self.client.logout();self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).status_code,401)
  from .models import Rol
  self.u.rol=Rol.objects.create(nombre='Verificador colectivo',permisos=['ausencias.ver','ausencias.ver_equipo']);self.u.save();self.client.force_login(self.u);self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).status_code,403)
 def test_cero_disponibilidad_no_influye_en_denominador(self):
  self.second();cal=CalendarioFuncionario.objects.get(funcionario=self.worker,periodo=self.p);cal.semana=['No laboral']*7;cal.save();r=self.result();self.assertEqual(r['items'][0]['meta'],'10.00');self.assertEqual(r['evaluados'],1)
 def test_pesos_incompatibles_y_cero_no_inventan_indice(self):
  from .collective import consolidate
  import copy
  self.activity();one=self.summary();two=copy.deepcopy(one);two['funcionario']=999;two['metas'][0]['ponderacion']='30'
  r=consolidate([one,two]);self.assertFalse(r['pesos_compatibles']);self.assertIsNone(r['cumplimiento']);self.assertEqual(r['items'][0]['cumplimiento'],'10.00')
  one['metas'][0]['ponderacion']='0';self.assertIsNone(consolidate([one])['cumplimiento'])
 summary=fixtures.PerformanceTests.summary
