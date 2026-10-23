from decimal import Decimal
from datetime import date,timedelta
from django.utils import timezone
from django.test import TestCase
from . import test_absences as helpers
from .models import Actividad,Evidencia,RevisionEvidencia,Usuario,Delegacion,ItemMeta,ConfiguracionMeta

class PerformanceTests(TestCase):
 send=helpers.AbsenceTests.send
 calendar=helpers.AbsenceTests.calendar
 absence=helpers.AbsenceTests.absence
 summary=helpers.AbsenceTests.summary
 def setUp(self):
  helpers.AbsenceTests.setUp(self);self.m.meta_esperada=Decimal('10');self.m.ponderacion=Decimal('20');self.m.save();self.cal=self.calendar()
 def activity(self,**extra):
  values=dict(autor=self.worker,delegacion=self.d,item=self.i,fecha=date(2026,2,3)+timedelta(days=Actividad.objects.count()//7),solicitud='Actividad ficticia',accion='Ejecución final',contacto='Persona ficticia',telefono='912345678',sector='QA',estado='Validada',elegibilidad_snapshot={'potencialmente_puntuable':True,'motivos':[],'clasificacion':'Ejecución','estado':'Potencialmente puntuable'})|extra
  a=Actividad.objects.create(**values);e=Evidencia.objects.create(actividad=a,autor=self.worker,delegacion=self.d,archivo='qa.pdf',nombre_archivo='qa.pdf',tipo_mime='application/pdf',tamano=12,sha256='a'*64,descripcion='QA',estado='Aprobada',version=2);RevisionEvidencia.objects.create(evidencia=e,autor=self.u,decision='Aprobada',observacion='Verificada',version_evidencia=2);return a
 def row(self):return self.summary()['metas'][0]
 def test_tope120_sin_borrar_registros_y_ponderado(self):
  for _ in range(13):self.activity()
  r=self.row();self.assertEqual(r['total_registrado'],13);self.assertEqual(r['validas'],13);self.assertEqual(r['unidades_reconocidas'],'12.00');self.assertEqual(r['exceso_tope'],'1.00');self.assertEqual(r['cumplimiento'],'120.00');self.assertEqual(r['aporte_ponderado'],'24.00');self.assertEqual(Actividad.objects.count(),13);self.assertEqual(r['aportes'][-1]['reconocido'],'0.00')
 def test_cruce_fraccionario_no_redondea_meta(self):
  self.m.meta_esperada=Decimal('10.5');self.m.save()
  for _ in range(13):self.activity()
  r=self.row();self.assertEqual(r['unidades_reconocidas'],'12.60');self.assertEqual(r['exceso_tope'],'0.40');self.assertEqual(r['aportes'][-1]['reconocido'],'0.60');self.assertEqual(r['cumplimiento'],'120.00')
 def test_ajuste_por_ausencias_usa_meta_exacta(self):
  self.m.meta_esperada=Decimal('10');self.m.save();self.absence(self.cal)
  for _ in range(10):self.activity()
  r=self.row();self.assertEqual(r['meta_ajustada'],'7.50');self.assertEqual(r['unidades_reconocidas'],'9.00');self.assertEqual(r['cumplimiento'],'120.00')
 def test_excluidas_pendientes_y_multiples_respaldos_no_duplican(self):
  a=self.activity();e=Evidencia.objects.create(actividad=a,autor=self.worker,delegacion=self.d,archivo='b.pdf',nombre_archivo='b.pdf',tipo_mime='application/pdf',tamano=12,sha256='b'*64,descripcion='QA',estado='Aprobada',version=2);RevisionEvidencia.objects.create(evidencia=e,autor=self.u,decision='Aprobada',observacion='QA',version_evidencia=2)
  self.activity(estado='Pendiente');self.activity(elegibilidad_snapshot={'potencialmente_puntuable':False,'motivos':['Fuera de plazo']});self.activity(elegibilidad_snapshot=None)
  r=self.row();self.assertEqual(r['total_registrado'],4);self.assertEqual(r['validas'],1);self.assertEqual(r['unidades_reconocidas'],'1.00');self.assertEqual(r['cumplimiento'],'10.00')
 def test_validada_sin_revision_real_o_autorrevision_no_aporta(self):
  a=self.activity();a.evidencias.get().revisiones.all().delete();a=self.activity();r=a.evidencias.get().revisiones.get();r.autor=self.worker;r.save();self.assertEqual(self.row()['validas'],0)
 def test_aislamiento_por_funcionario_item_delegacion_y_fecha(self):
  self.activity();self.activity(autor=self.u);self.activity(fecha='2026-03-01');other=Delegacion.objects.create(codigo='PERF2',nombre='Otra');self.activity(delegacion=other);item=ItemMeta.objects.create(codigo='PERF2',nombre='Otro');self.activity(item=item);self.assertEqual(self.row()['total_registrado'],1)
 def test_cambio_de_evidencia_recalcula_sin_reescribir_cierre(self):
  a=self.activity();self.assertEqual(self.row()['validas'],1);e=a.evidencias.get();e.estado='Anulada';e.save();self.assertEqual(self.row()['validas'],0)
  e.estado='Aprobada';e.save();self.send(f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Cerrar resultado'));e.estado='Anulada';e.save();self.assertEqual(self.row()['validas'],1);self.assertEqual(self.summary()['fuente'],'Parámetros del cierre')
 def test_cero_y_sin_calendario_no_evalua(self):
  self.m.meta_esperada=0;self.m.save();self.activity();r=self.row();self.assertIsNone(r['cumplimiento']);self.assertEqual(r['unidades_reconocidas'],'0.00');self.assertEqual(r['semaforo'],'Sin exigibilidad')
 def test_historico_cerrado_no_recibe_calculo_inferido(self):
  self.activity();self.p.cerrado=True;self.p.parametros_cierre={'ajustes_ausencia':[{'delegacion':self.d.pk,'funcionario':self.worker.pk,'metas':[{'id':self.m.pk,'cumplimiento':None}]}]};self.p.save();self.assertIsNone(self.row()['cumplimiento'])


 def test_semaforo_objetivo_diario_y_umbral60(self):
  from unittest.mock import patch
  for _ in range(3):self.activity()
  with patch('django.utils.timezone.localdate',return_value=date(2026,2,13)):
   r=self.row();self.assertEqual(self.summary()['objetivo_al_dia'],'50.00');self.assertEqual(r['semaforo'],'Naranjo')
   self.activity();self.activity();self.assertEqual(self.row()['semaforo'],'Verde')
  with patch('django.utils.timezone.localdate',return_value=date(2026,1,31)):self.assertEqual(self.row()['semaforo'],'Sin jornada transcurrida')
 def test_sin_calendario_cuenta_registros_pero_no_inventa_cumplimiento(self):
  from .models import CalendarioFuncionario
  CalendarioFuncionario.objects.filter(pk=self.cal['id']).delete();self.activity();r=self.row();self.assertEqual(r['total_registrado'],1);self.assertIsNone(r['cumplimiento']);self.assertEqual(r['semaforo'],'Sin calendario')


 def test_no_prorrateable_con_cero_disponibilidad_no_se_evalua(self):
  r=self.send(f"/api/ausencias/calendarios/{self.cal['id']}/",dict(_version=self.cal['version'],semana=['No laboral']*7,metas_prorrateables=[],confirmado=True,motivo='Sin jornadas previstas'),'patch');self.assertEqual(r.status_code,200,r.content);self.activity();r=self.row();self.assertIsNone(r['cumplimiento']);self.assertIsNone(r['aporte_ponderado']);self.assertEqual(r['unidades_reconocidas'],'0.00');self.assertEqual(r['semaforo'],'Sin jornada disponible')

from django.test import TransactionTestCase,Client
from django.db import close_old_connections
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import patch
class ConcurrentPerformanceTests(TransactionTestCase):
 send=helpers.AbsenceTests.send
 calendar=helpers.AbsenceTests.calendar
 setUp=PerformanceTests.setUp
 activity=PerformanceTests.activity
 def test_cierre_precede_validacion_sin_cambiar_snapshot(self):
  from . import absences
  self.role.permisos+=['evidencias.revisar','evidencias.ver_equipo'];self.role.save()
  a=self.activity(estado='Pendiente');e=a.evidencias.get();e.estado='Pendiente';e.version=1;e.save();e.revisiones.all().delete()
  clients=[]
  for _ in range(2):
   c=Client();c.force_login(self.u);clients.append(c)
  closing=Event();release=Event();finished=Event();original=absences.closure
  def paused(period):closing.set();release.wait(5);return original(period)
  def call(index,url,data):
   close_old_connections()
   try:return clients[index].post(url,data,content_type='application/json').status_code
   finally:
    if index==1:finished.set()
    close_old_connections()
  with patch('core.absences.closure',side_effect=paused),ThreadPoolExecutor(max_workers=2) as pool:
   close=pool.submit(call,0,f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Cierre concurrente'))
   try:
    self.assertTrue(closing.wait(5));review=pool.submit(call,1,f'/api/operacion/evidencias/{e.pk}/revisar/',dict(_version=e.version,decision='Aprobada',observacion='Validación concurrente'))
    finished.wait(.5)
   finally:release.set()
   self.assertEqual(close.result(),200);self.assertEqual(review.result(),200)
  self.p.refresh_from_db();a.refresh_from_db();self.assertEqual(a.estado,'Validada');self.assertEqual(self.p.parametros_cierre['ajustes_ausencia'][0]['metas'][0]['validas'],0)
