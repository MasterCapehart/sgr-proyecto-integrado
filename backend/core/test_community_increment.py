from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from . import test_community as community_tests, test_milestones as milestone_tests

class CommunityIncrementTests(TestCase):
 setUp=community_tests.CommunityTests.setUp
 send=community_tests.CommunityTests.send
 neighbor=community_tests.CommunityTests.neighbor
 org=community_tests.CommunityTests.org
 def test_identidad_separada_correo_y_nombre_historico(self):
  import uuid
  data=dict(nombres='Ana María',apellidos='Pérez Soto',correo='ANA@example.cl',clave_idempotencia=uuid.uuid4().hex)
  r=self.send('/api/vecinos/',data);self.assertEqual(r.status_code,201,r.content)
  v=r.json()['data'];self.assertEqual(v['nombre'],'Ana María Pérez Soto');self.assertEqual(v['correo'],'ana@example.cl')
  data['clave_idempotencia']=uuid.uuid4().hex;data['correo']='ana@EXAMPLE.CL';self.assertEqual(self.send('/api/vecinos/',data).status_code,409)
  data['correo']='correo inválido';self.assertEqual(self.send('/api/vecinos/',data).status_code,400)
  historical=self.neighbor();self.assertEqual(historical['apellidos'],'')
 def test_codigo_organizacion_y_cargo_fecha_participacion(self):
  o=self.org();self.assertTrue(o['codigo']);v=self.neighbor()
  r=self.send('/api/pertenencias/',dict(vecino=v['id'],organizacion=o['id'],rol='Dirigente',cargo_especifico='Presidenta',fecha_incorporacion='2024-03-10'))
  self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['fecha_incorporacion'],'2024-03-10')
  self.assertEqual(self.send(f'/api/organizaciones/{o["id"]}/',dict(_version=o['version'],codigo='inyectado'),'patch').status_code,400)

 def test_correo_edicion_scope_y_validacion_no_cambia_historia(self):
  import uuid
  a=self.neighbor();b=self.neighbor()
  r=self.send(f'/api/vecinos/{a["id"]}/',dict(_version=a['version'],correo='directorio@example.cl'),'patch');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(self.send(f'/api/vecinos/{b["id"]}/',dict(_version=b['version'],correo='DIRECTORIO@example.cl'),'patch').status_code,409)
  self.assertEqual(self.send(f'/api/vecinos/{b["id"]}/',dict(_version=b['version'],nombres=42),'patch').status_code,400)
  self.assertEqual(self.send(f'/api/vecinos/{b["id"]}/',dict(_version=b['version'],correo='sin arroba'),'patch').status_code,400)
  session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save()
  r=self.send('/api/vecinos/',dict(nombre='Otra delegación',correo='directorio@example.cl',clave_idempotencia=uuid.uuid4().hex));self.assertEqual(r.status_code,201,r.content)
 def test_fechas_participacion_y_timestamps_no_editables(self):
  o=self.org();v=self.neighbor();self.assertTrue(o['modificado'])
  data=dict(vecino=v['id'],organizacion=o['id'],rol='Integrante',fecha_incorporacion='no-fecha')
  self.assertEqual(self.send('/api/pertenencias/',data).status_code,400)
  self.assertEqual(self.send(f'/api/organizaciones/{o["id"]}/',dict(_version=o['version'],modificado='2000-01-01'),'patch').status_code,400)

class MilestoneIncrementTests(TestCase):
 setUp=milestone_tests.MilestoneTests.setUp
 send=milestone_tests.MilestoneTests.send
 payload=milestone_tests.MilestoneTests.payload
 hito=milestone_tests.MilestoneTests.hito
 task=milestone_tests.MilestoneTests.task
 def test_alertas_consultadas_no_crean_realizaciones(self):
  from .models import Hito
  h=self.hito();obj=Hito.objects.get(pk=h['id']);obj.fecha_inicio=timezone.localdate()+timedelta(days=3);obj.fecha_termino=obj.fecha_inicio;obj.save()
  r=self.client.get('/api/hitos/?alerta=Próximo');self.assertEqual(r.json()['count'],1);self.assertEqual(r.json()['results'][0]['alerta'],'Próximo');self.assertTrue(r.json()['results'][0]['codigo'])
  obj.fecha_inicio=timezone.localdate()-timedelta(days=4);obj.fecha_termino=obj.fecha_inicio;obj.save()
  self.assertEqual(self.client.get('/api/hitos/?alerta=Vencido').json()['count'],1);self.assertEqual(Hito.objects.count(),1)
 def test_desactivacion_con_motivo_conserva_historial(self):
  h=self.hito();t=self.task(h)
  r=self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],activo=False,motivo='Programación suspendida'),'patch')
  self.assertEqual(r.status_code,200,r.content);self.assertFalse(r.json()['data']['activo']);self.assertEqual(len(r.json()['data']['tareas']),1)
  self.assertEqual(self.send(f'/api/hitos/tareas/{t["id"]}/avances/',dict(_version=t['version'],porcentaje=10,observacion='No permitido')).status_code,400)

 def test_desactivacion_exige_motivo_version_y_lectura_responsable(self):
  h=self.hito()
  for extra in [dict(activo=False,motivo=''),dict(activo='false',motivo='Texto')]:
   self.assertEqual(self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],**extra),'patch').status_code,400)
  self.assertEqual(self.send(f'/api/hitos/{h["id"]}/',dict(_version=0,activo=False,motivo='Texto'),'patch').status_code,409)
  self.assertEqual(self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],codigo='alterado'),'patch').status_code,400)
  self.assertTrue(h['creado']);self.assertTrue(h['modificado'])

 def test_cierre_hito_tubo_exige_terminal_sin_fingir_ejecucion(self):
  from .models import Compromiso
  h=self.hito();t=self.task(h)
  self.send(f'/api/hitos/tareas/{t["id"]}/tubo/',dict(_version=t['version']))
  c=Compromiso.objects.get();self.assertIsNotNone(c.registro_gestion_id)
  c.estado='Realizado';c.save()
  self.assertEqual(self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],estado='Finalizado'),'patch').status_code,400)
  r=self.send(f'/api/operacion/compromisos/{c.pk}/',dict(_version=c.version,estado='No aplica',resultado='Actividad no requerida en esta realización',observacion='Decisión de cierre'),'patch');self.assertEqual(r.status_code,200,r.content)
  r=self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],estado='Finalizado'),'patch')
  self.assertEqual(r.status_code,200,r.content);self.assertEqual(r.json()['data']['tareas'][0]['porcentaje'],0)
