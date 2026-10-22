from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch
from django.test import TestCase,TransactionTestCase,Client
from django.db import close_old_connections
from concurrent.futures import ThreadPoolExecutor
from . import test_eligibility as helpers
from .models import Actividad,Compromiso,Atencion

def clock(day):return patch('django.utils.timezone.now',return_value=datetime.fromisoformat(day+'T12:00:00').replace(tzinfo=ZoneInfo('America/Santiago')))

class RegistrationLimitTests(TestCase):
 setUp=helpers.EligibilityTests.setUp
 payload=helpers.EligibilityTests.payload
 activity=helpers.EligibilityTests.activity
 send=helpers.EligibilityTests.send
 rule=helpers.EligibilityTests.rule
 def create(self,day='2026-01-05',**kw):
  p=self.payload();p['actividad'].update(fecha=day,**kw);return self.send('/api/captura/',p)
 def edit(self,a,**kw):return self.send(f'/api/operacion/actividades/{a["id"]}/',dict(_version=a['version'],**kw),'patch')
 def test_tres_dias_inclusivos_y_tardio_conservado(self):
  self.rule()
  for registered,eligible in [('2026-01-05',True),('2026-01-07',True),('2026-01-08',False)]:
   with clock(registered):r=self.create()
   self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['elegibilidad']['potencialmente_puntuable'],eligible)
  self.assertIn('fuera de plazo',' '.join(r.json()['data']['elegibilidad']['motivos']))
 def test_fin_de_semana_y_cambio_de_ano(self):
  self.rule()
  for day,registered,eligible in [('2026-01-09','2026-01-11',True),('2026-01-09','2026-01-12',False),('2025-12-31','2026-01-02',True),('2025-12-31','2026-01-03',False)]:
   with clock(registered):r=self.create(day)
   self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['elegibilidad']['potencialmente_puntuable'],eligible)
 def test_octava_bloqueada_y_reintento_no_consume_otro(self):
  self.rule()
  with clock('2026-01-05'):
   for _ in range(7):self.assertEqual(self.create().status_code,201)
   r=self.create();self.assertEqual(r.status_code,409,r.content);self.assertIn('7',r.json()['error']['message']);self.assertEqual(Actividad.objects.count(),7)
 def test_exclusiones_y_tardios_no_consumen_cupo(self):
  self.rule()
  with clock('2026-01-08'):
   for _ in range(9):self.assertEqual(self.create().status_code,201)
   for _ in range(9):self.assertEqual(self.create('2026-01-08',telefono='').status_code,201)
   for _ in range(7):self.assertEqual(self.create('2026-01-08').status_code,201)
   self.assertEqual(self.create('2026-01-08').status_code,409)
 def test_libera_y_recupera_solo_si_hay_cupo(self):
  self.rule()
  with clock('2026-01-05'):
   records=[self.create().json()['data'] for _ in range(7)]
   r=self.edit(records[0],telefono='');self.assertEqual(r.status_code,200,r.content);released=r.json()['data'];self.assertFalse(released['elegibilidad']['potencialmente_puntuable'])
   self.assertEqual(self.create().status_code,201)
   self.assertEqual(self.edit(released,telefono='912345678').status_code,409)
 def test_datos_completados_tarde_no_habilitan_y_texto_no_quita_cupo(self):
  self.rule()
  with clock('2026-01-05'):
   incomplete=self.create(telefono='').json()['data'];eligible=self.create().json()['data']
  with clock('2026-01-08'):
   r=self.edit(incomplete,telefono='912345678');self.assertEqual(r.status_code,200,r.content);self.assertFalse(r.json()['data']['elegibilidad']['potencialmente_puntuable'])
   r=self.edit(eligible,accion='Texto corregido después del plazo');self.assertEqual(r.status_code,200,r.content);self.assertTrue(r.json()['data']['elegibilidad']['potencialmente_puntuable'])
 def test_fecha_inmutable_y_fecha_registro_no_inyectable(self):
  self.rule()
  with clock('2026-01-07'):
   a=self.create().json()['data'];r=self.edit(a,fecha='2026-01-07');self.assertEqual(r.status_code,400,r.content)
   p=self.payload();p['actividad']['creado']='2026-01-05';self.assertEqual(self.send('/api/captura/',p).status_code,400)
 def test_octava_revierte_social_y_compromiso(self):
  self.rule()
  with clock('2026-01-05'):
   for _ in range(7):self.create()
   p=self.payload();p['actividad']['fecha']='2026-01-05';p['social']=dict(tipo_atencion=self.t.pk,sub_atencion=self.s.pk,nuevo_caso=True);p['nuevo_compromiso']=dict(responsable=self.u.pk,fecha_comprometida='2026-01-06')
   r=self.send('/api/captura/',p);self.assertEqual(r.status_code,409,r.content);self.assertEqual(Compromiso.objects.count(),0);self.assertEqual(Atencion.objects.count(),0)
 def test_via_operacion_tambien_aplica_cupo(self):
  self.rule()
  with clock('2026-01-05'):
   for _ in range(7):self.create()
   data=self.activity(fecha='2026-01-05');self.assertEqual(self.send('/api/operacion/actividades/',data).status_code,409)

 def test_cupo_compartido_entre_delegaciones(self):
  self.rule()
  with clock('2026-01-05'):
   for _ in range(4):self.create()
   session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save();self.rule()
   for _ in range(3):self.assertEqual(self.create().status_code,201)
   self.assertEqual(self.create().status_code,409)
 def test_historicos_cuentan_sin_reclasificacion_retroactiva(self):
  self.rule()
  with clock('2026-01-05'):
   rows=[self.create().json()['data'] for _ in range(7)]
   for row in rows:
    obj=Actividad.objects.get(pk=row['id']);obj.elegibilidad_snapshot.pop('control_registro');obj.cupo_diario_reservado=False;obj.save()
   self.assertEqual(self.create().status_code,409)
   old=Actividad.objects.get(pk=rows[0]['id']);r=self.edit(rows[0],accion='Nota histórica');self.assertEqual(r.status_code,200,r.content);self.assertNotIn('control_registro',r.json()['data']['elegibilidad'])
   r=self.edit(r.json()['data'],telefono='');self.assertEqual(r.status_code,200);self.assertEqual(self.create().status_code,201)
 def test_fecha_local_de_santiago_en_lugar_de_fecha_utc(self):
  self.rule()
  # UTC Thursday01:00 is still Wednesday22:00 in Santiago: Monday remains in time.
  with patch('django.utils.timezone.now',return_value=datetime(2026,1,8,1,0,tzinfo=ZoneInfo('UTC'))):r=self.create()
  self.assertEqual(r.status_code,201,r.content);self.assertTrue(r.json()['data']['elegibilidad']['potencialmente_puntuable']);self.assertEqual(r.json()['data']['elegibilidad']['control_registro']['fecha_registro'],'2026-01-07')
 def test_preview_no_reserva_y_muestra_cupos_antes_de_guardar(self):
  self.rule()
  with clock('2026-01-05'):
   r=self.send('/api/clasificacion-actividades/evaluar/',dict(fecha='2026-01-05',item=self.i.pk,contacto='Persona ficticia',telefono='912345678'));self.assertEqual(r.status_code,200,r.content);control=r.json()['data']['control_registro'];self.assertFalse(control['reserva_cupo']);self.assertEqual(control['cupo_disponible_al_evaluar'],7);self.assertEqual(Actividad.objects.count(),0)

class ConcurrentRegistrationLimitTests(TransactionTestCase):
 setUp=helpers.EligibilityTests.setUp
 payload=helpers.EligibilityTests.payload
 activity=helpers.EligibilityTests.activity
 send=helpers.EligibilityTests.send
 rule=helpers.EligibilityTests.rule
 def test_ultima_reserva_simultanea_no_excede_siete(self):
  self.rule()
  with clock('2026-01-05'):
   for _ in range(6):
    p=self.payload();p['actividad']['fecha']='2026-01-05';self.assertEqual(self.send('/api/captura/',p).status_code,201)
   payloads=[self.payload(),self.payload()]
   for p in payloads:p['actividad']['fecha']='2026-01-05'
   uid=self.u.pk
   def create(data):
    close_old_connections()
    try:
     from .models import Usuario
     client=Client();client.force_login(Usuario.objects.get(pk=uid));return client.post('/api/captura/',data,content_type='application/json').status_code
    finally:close_old_connections()
   with ThreadPoolExecutor(max_workers=2) as pool:statuses=list(pool.map(create,payloads))
   self.assertEqual(sorted(statuses),[201,409]);self.assertEqual(Actividad.objects.count(),7)

 def test_primeras_capturas_simultaneas_crean_un_solo_control(self):
  self.rule();uid=self.u.pk
  with clock('2026-01-05'):
   data=[self.payload() for _ in range(5)]
   for p in data:p['actividad']['fecha']='2026-01-05'
   def create(p):
    close_old_connections()
    try:
     from .models import Usuario
     client=Client();client.force_login(Usuario.objects.get(pk=uid));return client.post('/api/captura/',p,content_type='application/json').status_code
    finally:close_old_connections()
   with ThreadPoolExecutor(max_workers=5) as pool:statuses=list(pool.map(create,data))
   self.assertEqual(statuses,[201]*5)
   from .models import ControlCupoFuncionario
   self.assertEqual(ControlCupoFuncionario.objects.filter(usuario_id=uid).count(),1)
