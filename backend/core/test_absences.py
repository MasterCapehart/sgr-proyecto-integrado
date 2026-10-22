from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from .models import Usuario,Rol,Delegacion,PeriodoGestion,ItemMeta,ConfiguracionMeta

class AbsenceTests(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='AUS',nombre='Ausencias QA');self.role=Rol.objects.create(nombre='Delegado',permisos=['ausencias.ver','ausencias.ver_equipo','ausencias.gestionar','periodos.cerrar','periodos.reabrir']);self.u=Usuario.objects.create_user('delegado_aus',rol=self.role,delegacion=self.d);self.client.force_login(self.u)
  self.worker=Usuario.objects.create_user('func_aus',rol=Rol.objects.create(nombre='Funcionario',permisos=['ausencias.ver']),delegacion=self.d)
  self.p=PeriodoGestion.objects.create(codigo='FEB26',nombre='Febrero prueba',fecha_inicio='2026-02-02',fecha_fin='2026-02-27');self.i=ItemMeta.objects.create(codigo='AUS',nombre='Ítem ausencias');self.m=ConfiguracionMeta.objects.create(item=self.i,periodo_gestion=self.p,periodo=self.p.codigo,meta_esperada=100)
 def send(self,url,data,method='post'):return getattr(self.client,method)(url,data,content_type='application/json')
 def calendar(self,**extra):
  p=dict(funcionario=self.worker.pk,periodo=self.p.pk,semana=['Completa']*5+['No laboral']*2,no_laborables=[],metas_prorrateables=[self.m.pk],confirmado=True,motivo='Calendario de prueba confirmado')|extra
  r=self.send('/api/ausencias/calendarios/',p);self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def absence(self,cal,**extra):
  p=dict(calendario=cal['id'],tipo='Vacaciones',inicio='2026-02-02',fin='2026-02-06',jornada='Completa',justificacion='Ausencia autorizada sin datos clínicos')|extra
  r=self.send('/api/ausencias/',p);self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def summary(self):
  r=self.client.get(f'/api/ausencias/resumen/?funcionario={self.worker.pk}&periodo={self.p.pk}');self.assertEqual(r.status_code,200,r.content);return r.json()['data']
 def test_sin_calendario_no_inventa_meta_ajustada(self):
  r=self.summary();self.assertEqual(r['estado'],'Sin calendario');self.assertIsNone(r['metas'][0]['meta_ajustada'])
 def test_veinte_dias_cinco_ausencia_meta_75(self):
  cal=self.calendar();self.absence(cal);r=self.summary();self.assertEqual(r['dias_previstos'],'20.00');self.assertEqual(r['dias_ausencia'],'5.00');self.assertEqual(r['metas'][0]['meta_ajustada'],'75.00');self.m.refresh_from_db();self.assertEqual(self.m.meta_esperada,Decimal('100'))
 def test_solapamientos_no_se_descontabilizan_doble(self):
  cal=self.calendar();self.absence(cal);self.absence(cal,inicio='2026-02-04',fin='2026-02-08');self.assertEqual(self.summary()['dias_ausencia'],'5.00')
 def test_medios_dias_y_jornadas_parciales(self):
  cal=self.calendar(semana=['Mañana']*5+['No laboral']*2);self.absence(cal,jornada='Tarde');self.assertEqual(self.summary()['dias_ausencia'],'0.00');self.absence(cal,jornada='Mañana');r=self.summary();self.assertEqual(r['dias_previstos'],'10.00');self.assertEqual(r['dias_ausencia'],'2.50');self.assertEqual(r['metas'][0]['meta_ajustada'],'75.00')
 def test_feriados_y_recorte_al_periodo(self):
  cal=self.calendar(no_laborables=['2026-02-02']);self.absence(cal,inicio='2026-01-20',fin='2026-02-03');r=self.summary();self.assertEqual(r['dias_previstos'],'19.00');self.assertEqual(r['dias_ausencia'],'1.00');self.assertEqual(r['metas'][0]['meta_ajustada'],'94.74')
 def test_cero_jornada_y_ausencia_total_no_incumplimiento(self):
  cal=self.calendar(semana=['No laboral']*7);r=self.summary();self.assertEqual(r['estado'],'Sin jornada prevista');self.assertIsNone(r['metas'][0]['meta_ajustada'])
  r=self.send(f"/api/ausencias/calendarios/{cal['id']}/",dict(_version=cal['version'],semana=['Completa']*5+['No laboral']*2,confirmado=True,motivo='Corregir jornada'),'patch');self.assertEqual(r.status_code,200,r.content);self.absence(r.json()['data'],fin='2026-02-27');r=self.summary();self.assertEqual(r['estado'],'Sin exigibilidad por ausencia');self.assertEqual(r['metas'][0]['meta_ajustada'],'0.00')
 def test_meta_no_proporcional_conserva_base(self):
  cal=self.calendar(metas_prorrateables=[]);self.absence(cal);self.assertEqual(self.summary()['metas'][0]['meta_ajustada'],'100.00')
 def test_calendario_exige_confirmacion_y_referencias_validas(self):
  p=dict(funcionario=self.worker.pk,periodo=self.p.pk,semana=['Completa']*7,no_laborables=[],metas_prorrateables=[self.m.pk],confirmado=False,motivo='QA');self.assertEqual(self.send('/api/ausencias/calendarios/',p).status_code,400)
  p['confirmado']=True;p['no_laborables']=['2027-01-01'];self.assertEqual(self.send('/api/ausencias/calendarios/',p).status_code,400)
 def test_anulacion_versionada_y_auditada(self):
  cal=self.calendar();a=self.absence(cal);r=self.send(f"/api/ausencias/{a['id']}/",dict(_version=a['version'],estado='Anulada',justificacion='Registro duplicado anulado'),'patch');self.assertEqual(r.status_code,200,r.content);self.assertEqual(self.summary()['dias_ausencia'],'0.00');self.assertTrue(r.json()['data']['historial']);self.assertEqual(self.send(f"/api/ausencias/{a['id']}/",dict(_version=a['version'],estado='Autorizada',justificacion='Restituir'),'patch').status_code,409)
 def test_periodo_cerrado_bloquea_y_conserva_snapshot(self):
  cal=self.calendar();a=self.absence(cal);r=self.send(f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Cierre de prueba'));self.assertEqual(r.status_code,200,r.content);self.p.refresh_from_db();self.assertIn('ajustes_ausencia',self.p.parametros_cierre)
  self.assertEqual(self.send(f"/api/ausencias/{a['id']}/",dict(_version=a['version'],estado='Anulada',justificacion='No permitido'),'patch').status_code,400)
  p=dict(calendario=cal['id'],tipo='Día libre',inicio='2026-02-10',fin='2026-02-10',jornada='Completa',justificacion='No permitido');self.assertEqual(self.send('/api/ausencias/',p).status_code,400)
 def test_funcionario_ve_solo_propio_sin_gestionar(self):
  cal=self.calendar();self.absence(cal);self.client.force_login(self.worker);self.assertEqual(self.summary()['dias_ausencia'],'5.00');self.assertEqual(self.send('/api/ausencias/',{}).status_code,403);self.assertEqual(self.client.get(f'/api/ausencias/resumen/?funcionario={self.u.pk}&periodo={self.p.pk}').status_code,404)
 def test_fuera_de_delegacion_y_permisos_no_habilitan_otro_rol(self):
  other=Delegacion.objects.create(codigo='AUS2',nombre='Ajena');self.worker.delegacion=other;self.worker.save();r=self.client.get(f'/api/ausencias/resumen/?funcionario={self.worker.pk}&periodo={self.p.pk}');self.assertEqual(r.status_code,404)
  self.u.rol=Rol.objects.create(nombre='Verificador',permisos=self.role.permisos);self.u.save();self.assertEqual(self.send('/api/ausencias/calendarios/',{}).status_code,403)
 def test_cierre_no_expone_disponibilidad_en_catalogo_general(self):
  from . import local_api,catalog_history
  cal=self.calendar();self.absence(cal);r=self.send(f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Cierre privado'));self.assertEqual(r.status_code,200,r.content);self.p.refresh_from_db()
  self.assertIn('ajustes_ausencia',self.p.parametros_cierre);self.assertNotIn('ajustes_ausencia',r.json()['data']['parametros_cierre']);self.assertNotIn('ajustes_ausencia',catalog_history.catalog(self.p)['parametros_cierre'])
 def test_fuente_cerrada_conserva_ajuste_aunque_cargo_cambie(self):
  cal=self.calendar();self.absence(cal);self.send(f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Cierre'));self.assertEqual(self.summary()['fuente'],'Parámetros del cierre');self.i.estado=False;self.i.save();self.assertEqual(self.summary()['metas'][0]['meta_ajustada'],'75.00')

 def test_cierre_sin_calendario_no_reconstruye_metas_con_catalogo_actual(self):
  self.send(f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Cierre sin jornada'));self.assertEqual(self.summary()['metas'],[])

from django.test import TransactionTestCase,Client
from django.db import close_old_connections
from concurrent.futures import ThreadPoolExecutor
class ConcurrentAbsenceTests(TransactionTestCase):
 setUp=AbsenceTests.setUp
 send=AbsenceTests.send
 calendar=AbsenceTests.calendar
 def test_cierre_y_alta_se_serializan_sin_alterar_cierre(self):
  cal=self.calendar();clients=[]
  for _ in range(2):
   c=Client();c.force_login(self.u);clients.append(c)
  requests=[(f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Cierre concurrente')),
   ('/api/ausencias/',dict(calendario=cal['id'],tipo='Vacaciones',inicio='2026-02-02',fin='2026-02-06',jornada='Completa',justificacion='Ausencia concurrente'))]
  def send(args):
   client,(url,data)=args;close_old_connections()
   try:return client.post(url,data,content_type='application/json').status_code
   finally:close_old_connections()
  with ThreadPoolExecutor(max_workers=2) as pool:statuses=list(pool.map(send,zip(clients,requests)))
  self.assertEqual(statuses[0],200);self.assertIn(statuses[1],[201,400]);self.p.refresh_from_db();result=self.p.parametros_cierre['ajustes_ausencia'][0]
  self.assertEqual(result['metas'][0]['meta_ajustada'],'75.00' if statuses[1]==201 else '100.00')
