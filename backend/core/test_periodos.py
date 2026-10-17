"""PAR-01/04/05: calendario, parámetros históricos y cierre autorizado."""
from datetime import date
from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from .models import Usuario, Rol, PeriodoGestion, ItemMeta, ConfiguracionMeta, EventoLocal, Delegacion

class PeriodosTests(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='PER',nombre='Delegación de períodos QA')
  self.u=Usuario.objects.create_superuser('periodos','periodos@example.test','ClavePeriodo!7261',delegacion=self.d);self.client.force_login(self.u)
  self.item=ItemMeta.objects.create(codigo='PER',nombre='Ítem períodos')
 def send(self,path,data,method='post'):return getattr(self.client,method)(path,data,content_type='application/json')
 def period(self,**changes):
  r=self.send('/api/periodos/',{'codigo':'P01','nombre':'Primer trimestre QA','fecha_inicio':'2028-01-01','fecha_fin':'2028-03-31',**changes});self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def meta(self,p):
  r=self.send('/api/configuraciones-metas/',{'item':self.item.pk,'periodo_gestion':p['id'],'meta_esperada':10,'ponderacion':20});self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_calendario_real_bisiesto_y_dias_inclusivos(self):
  p=self.period();self.assertEqual(p['duracion_dias'],91)
  p=self.period(codigo='P02',nombre='Trimestre no bisiesto',fecha_inicio='2027-01-01',fecha_fin='2027-03-31');self.assertEqual(p['duracion_dias'],90)
 def test_fechas_invertidas_formato_y_vacias_rechazadas(self):
  for change in [{'fecha_fin':'2027-01-01'},{'fecha_inicio':'no-fecha'},{'fecha_inicio':''}]:
   self.assertEqual(self.send('/api/periodos/',{'codigo':'P01','nombre':'QA','fecha_inicio':'2028-01-01','fecha_fin':'2028-03-31',**change}).status_code,400)
  self.assertEqual(PeriodoGestion.objects.count(),0)
 def test_solo_acciones_con_permiso_y_version(self):
  p=self.period();self.assertEqual(self.send(f"/api/periodos/{p['id']}/cerrar/",{'motivo':'Prueba'}).status_code,428)
  self.assertEqual(self.send(f"/api/periodos/{p['id']}/cerrar/",{'_version':0,'motivo':'Prueba'}).status_code,409)
  role=Rol.objects.create(nombre='Consulta períodos',permisos=['periodos.ver']);u=Usuario.objects.create_user('lector_periodo',rol=role);self.client.force_login(u)
  self.assertEqual(self.client.get('/api/periodos/').status_code,200)
  self.assertEqual(self.send('/api/periodos/',{}).status_code,403)
  self.assertEqual(self.send(f"/api/periodos/{p['id']}/cerrar/",{'_version':p['version'],'motivo':'Prueba'}).status_code,403)
 def test_cierre_bloquea_meta_y_preserva_parametros(self):
  p=self.period();m=self.meta(p)
  r=self.send(f"/api/periodos/{p['id']}/cerrar/",{'_version':p['version'],'motivo':'Cierre de evaluación QA'});self.assertEqual(r.status_code,200,r.content);closed=r.json()['data']
  self.assertTrue(closed['cerrado']);self.assertEqual(closed['parametros_cierre']['metas'][0]['meta_esperada'],'10.00')
  url=f"/api/configuraciones-metas/{m['id']}/"
  for data in [{'meta_esperada':99},{'periodo_gestion':None},{'estado':False}]:
   self.assertEqual(self.send(url,{'_version':m['version'],**data},'patch').status_code,400)
  self.assertEqual(self.send(f"/api/periodos/{p['id']}/",{'_version':closed['version'],'fecha_fin':'2028-04-01'},'patch').status_code,400)
  self.assertEqual(self.send('/api/configuraciones-metas/',{'item':self.item.pk,'periodo_gestion':p['id'],'meta_esperada':20,'ponderacion':20}).status_code,400)
  saved=self.client.get(f"/api/periodos/{p['id']}/").json()['data'];self.assertEqual(saved['parametros_cierre'],closed['parametros_cierre'])
 def test_reapertura_motivo_auditoria_y_cambios_otra_version(self):
  p=self.period();m=self.meta(p)
  closed=self.send(f"/api/periodos/{p['id']}/cerrar/",{'_version':p['version'],'motivo':'Cierre QA'}).json()['data']
  self.assertEqual(self.send(f"/api/periodos/{p['id']}/reabrir/",{'_version':closed['version'],'motivo':' '}).status_code,400)
  opened=self.send(f"/api/periodos/{p['id']}/reabrir/",{'_version':closed['version'],'motivo':'Corrección autorizada QA'});self.assertEqual(opened.status_code,200,opened.content)
  self.assertFalse(opened.json()['data']['cerrado']);self.assertTrue(EventoLocal.objects.filter(recurso='periodos',accion='reabrir').exists())
  self.assertEqual(self.send(f"/api/configuraciones-metas/{m['id']}/",{'_version':m['version'],'meta_esperada':20},'patch').status_code,200)
  self.assertEqual(PeriodoGestion.objects.get(pk=p['id']).parametros_cierre['metas'][0]['meta_esperada'],'10.00')
  history=self.client.get(f"/api/periodos/{p['id']}/historial/");self.assertEqual(history.status_code,200,history.content);self.assertGreaterEqual(len(history.json()['results']),3)
 def test_nueva_meta_exige_periodo_existente_sin_inventar_fechas(self):
  data={'item':self.item.pk,'periodo':'2026-inventado','meta_esperada':10,'ponderacion':20}
  self.assertEqual(self.send('/api/configuraciones-metas/',data).status_code,400)
  self.assertEqual(PeriodoGestion.objects.count(),0)
 def test_periodo_textual_conocido_es_compatible(self):
  p=self.period();m=self.send('/api/configuraciones-metas/',{'item':self.item.pk,'periodo':p['codigo'],'meta_esperada':10,'ponderacion':20});self.assertEqual(m.status_code,201,m.content);self.assertEqual(m.json()['data']['periodo_gestion'],p['id'])
 def test_no_duplicar_meta_de_periodo_y_no_reasignar_historico_cerrado(self):
  p=self.period();m=self.meta(p)
  self.assertEqual(self.send('/api/configuraciones-metas/',{'item':self.item.pk,'periodo_gestion':p['id'],'meta_esperada':20,'ponderacion':30}).status_code,400)
  self.assertEqual(ConfiguracionMeta.objects.count(),1)
 def test_periodo_con_metas_no_desactivar_y_exportacion_filtrada(self):
  p=self.period();self.meta(p)
  self.assertEqual(self.send(f"/api/periodos/{p['id']}/toggle-estado/",{'_version':p['version']}).status_code,400)
  r=self.client.get('/api/periodos/export/?search=P01');self.assertEqual(r.status_code,200);self.assertTrue(r.content.startswith(b'PK'))
 def test_historico_sin_fechas_se_conserva_y_puede_vincularse(self):
  old=ConfiguracionMeta.objects.create(item=self.item,periodo='QA Histórico',meta_esperada=10,ponderacion=20)
  r=self.client.get(f'/api/configuraciones-metas/{old.pk}/');self.assertEqual(r.status_code,200);self.assertIsNone(r.json()['data']['periodo_gestion']);self.assertEqual(r.json()['data']['periodo'],'QA Histórico')
  p=self.period();r=self.send(f'/api/configuraciones-metas/{old.pk}/',{'_version':old.version,'periodo_gestion':p['id']},'patch');self.assertEqual(r.status_code,200,r.content)

 def test_calendarios_distintos_no_colisionan_por_etiqueta_historica(self):
  p=self.period();self.meta(p)
  r=self.send(f"/api/periodos/{p['id']}/",{'_version':p['version'],'codigo':'P-RENOMBRADO'},'patch');self.assertEqual(r.status_code,200,r.content)
  other=self.period(codigo='P01',nombre='Otro calendario QA',fecha_inicio='2029-01-01',fecha_fin='2029-03-31')
  self.meta(other)

class ConciliacionMetasTests(TestCase):
 def setUp(self):
  self.u=Usuario.objects.create_superuser('conciliador','conciliador@example.test','ClavePeriodo!7261');self.item=ItemMeta.objects.create(codigo='CON',nombre='Ítem conciliación')
 def row(self,period='QA',**kwargs):return ConfiguracionMeta.objects.create(item=self.item,periodo=period,meta_esperada=10,ponderacion=20,**kwargs)
 def run_command(self,apply=False):
  out=StringIO();call_command('conciliar_metas',apply=apply,usuario=self.u.username,motivo='Conciliación de prueba',stdout=out);return out.getvalue()
 def test_simulacion_no_modifica_y_aplicar_es_idempotente(self):
  a=self.row();b=self.row();self.run_command();b.refresh_from_db();self.assertIsNone(b.conciliada_con_id)
  self.run_command(True);b.refresh_from_db();self.assertEqual(b.conciliada_con_id,a.pk);self.assertFalse(b.estado);self.assertEqual(ConfiguracionMeta.objects.count(),2)
  count=EventoLocal.objects.filter(accion='conciliar').count();self.run_command(True);self.assertEqual(EventoLocal.objects.filter(accion='conciliar').count(),count)
 def test_unica_activa_prevalece_sin_cambiar_valores_anteriores(self):
  a=self.row();b=ConfiguracionMeta.objects.create(item=self.item,periodo='QA',meta_esperada=5,ponderacion=20,estado=False);self.run_command(True);b.refresh_from_db();self.assertEqual(b.conciliada_con_id,a.pk);self.assertEqual(b.meta_esperada,5)
 def test_ambiguos_no_se_concilian_automaticamente(self):
  a=self.row();b=ConfiguracionMeta.objects.create(item=self.item,periodo='QA',meta_esperada=99,ponderacion=20);self.run_command(True);a.refresh_from_db();b.refresh_from_db();self.assertIsNone(a.conciliada_con_id);self.assertIsNone(b.conciliada_con_id)
 def test_conciliada_no_se_reactiva_desde_api(self):
  a=self.row();b=self.row();self.run_command(True);self.client.force_login(self.u);b.refresh_from_db()
  r=self.client.post(f'/api/configuraciones-metas/{b.pk}/toggle-estado/',{'_version':b.version},content_type='application/json');self.assertEqual(r.status_code,400,r.content)

 def test_no_conciliar_metas_de_calendarios_distintos(self):
  p1=PeriodoGestion.objects.create(codigo='A',nombre='A',fecha_inicio=date(2026,1,1),fecha_fin=date(2026,3,31))
  p2=PeriodoGestion.objects.create(codigo='B',nombre='B',fecha_inicio=date(2027,1,1),fecha_fin=date(2027,3,31))
  a=self.row(periodo_gestion=p1);b=self.row(periodo_gestion=p2,estado=False)
  self.run_command(True);b.refresh_from_db();self.assertIsNone(b.conciliada_con_id)

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.test import TransactionTestCase, Client
from django.db import close_old_connections

class ConcurrenciaPeriodosTests(TransactionTestCase):
 def setUp(self):
  self.u=Usuario.objects.create_superuser('concurrente_periodo','periodo-concurrente@example.test','ClavePeriodo!7261')
  self.p=PeriodoGestion.objects.create(codigo='C01',nombre='Calendario concurrente',fecha_inicio=date(2026,1,1),fecha_fin=date(2026,12,31))
  self.item=ItemMeta.objects.create(codigo='C01',nombre='Ítem concurrente')
 def concurrent(self,operations):
  barrier=Barrier(len(operations))
  def worker(operation):
   close_old_connections()
   try:
    client=Client();client.force_login(Usuario.objects.get(pk=self.u.pk));barrier.wait(timeout=15)
    method,path,data=operation;return getattr(client,method)(path,data,content_type='application/json').status_code
   finally:close_old_connections()
  with ThreadPoolExecutor(max_workers=len(operations)) as pool:return list(pool.map(worker,operations))
 def test_dos_altas_misma_meta_no_duplican(self):
  data={'item':self.item.pk,'periodo_gestion':self.p.pk,'meta_esperada':10,'ponderacion':20}
  codes=self.concurrent([('post','/api/configuraciones-metas/',data)]*2)
  self.assertEqual(sorted(codes),[201,400]);self.assertEqual(ConfiguracionMeta.objects.count(),1)
 def test_cierre_y_alta_concurrentes_conservan_captura_coherente(self):
  codes=self.concurrent([('post','/api/configuraciones-metas/',{'item':self.item.pk,'periodo_gestion':self.p.pk,'meta_esperada':10,'ponderacion':20}),('post',f'/api/periodos/{self.p.pk}/cerrar/',{'_version':self.p.version,'motivo':'Cierre concurrente QA'})])
  self.assertIn(codes[0],[201,400]);self.assertEqual(codes[1],200);self.p.refresh_from_db();self.assertTrue(self.p.cerrado);self.assertEqual(len(self.p.parametros_cierre['metas']),ConfiguracionMeta.objects.count())
 def test_cierre_y_edicion_concurrentes_no_alteran_captura_cerrada(self):
  m=ConfiguracionMeta.objects.create(item=self.item,periodo=self.p.codigo,periodo_gestion=self.p,meta_esperada=10,ponderacion=20)
  codes=self.concurrent([('patch',f'/api/configuraciones-metas/{m.pk}/',{'_version':m.version,'meta_esperada':99}),('post',f'/api/periodos/{self.p.pk}/cerrar/',{'_version':self.p.version,'motivo':'Cierre con edición concurrente QA'})])
  self.assertIn(codes[0],[200,400]);self.assertEqual(codes[1],200);m.refresh_from_db();self.p.refresh_from_db();self.assertEqual(self.p.parametros_cierre['metas'][0]['meta_esperada'],str(m.meta_esperada))
