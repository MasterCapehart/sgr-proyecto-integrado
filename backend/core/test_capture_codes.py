from django.test import TestCase
from django.utils import timezone
from . import test_capture_form as helpers
from .models import Actividad,EventoLocal

class CaptureCodeTests(TestCase):
 setUp=helpers.CaptureFormTests.setUp
 activity=helpers.CaptureFormTests.activity
 payload=helpers.CaptureFormTests.payload
 post=helpers.CaptureFormTests.post
 def reserve(self):return self.client.post('/api/captura/reservar-codigo/',{'fecha':str(timezone.localdate())},content_type='application/json')
 def test_codigo_visible_es_el_guardado_y_reintento_no_duplica(self):
  r=self.reserve();self.assertEqual(r.status_code,200,r.content);v=r.json()['data'];self.assertFalse(Actividad.objects.exists())
  data=self.payload();data['_reserva_codigo']=v['reserva'];created=self.post(data);self.assertEqual(created.status_code,201,created.content)
  self.assertEqual(created.json()['data']['codigo'],v['codigo']);self.assertEqual(self.post(data).status_code,200)
 def test_dos_formularios_tienen_codigos_distintos(self):
  a=self.reserve();b=self.reserve();self.assertEqual(a.status_code,200,a.content);self.assertNotEqual(a.json()['data']['codigo'],b.json()['data']['codigo']);self.assertFalse(Actividad.objects.exists())
 def test_reserva_ajena_o_fecha_cambiada_se_rechazan(self):
  r=self.reserve();self.assertEqual(r.status_code,200,r.content);data=self.payload();data['_reserva_codigo']=r.json()['data']['reserva'];data['actividad']['fecha']='2026-01-01';self.assertEqual(self.post(data).status_code,400);self.assertFalse(Actividad.objects.exists())
  self.client.force_login(self.other);self.assertIn(self.post(data).status_code,[400,403]);self.assertFalse(Actividad.objects.exists())
 def test_error_de_captura_no_consume_reserva(self):
  r=self.reserve();self.assertEqual(r.status_code,200,r.content);data=self.payload();data['_reserva_codigo']=r.json()['data']['reserva'];data['actividad']['item']=999999
  self.assertEqual(self.post(data).status_code,400);event=EventoLocal.objects.filter(recurso='reserva_codigo').latest('id');self.assertFalse(event.despues['consumido'])

from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase,Client
from django.db import close_old_connections

class ConcurrentCaptureCodeTests(TransactionTestCase):
 setUp=CaptureCodeTests.setUp
 activity=CaptureCodeTests.activity
 payload=CaptureCodeTests.payload
 reserve=CaptureCodeTests.reserve
 def test_reintento_simultaneo_devuelve_el_mismo_codigo(self):
  reservation=self.reserve().json()['data'];data=self.payload();data['_reserva_codigo']=reservation['reserva']
  clients=[Client() for _ in range(3)]
  for c in clients:c.force_login(self.u)
  def submit(c):
   close_old_connections()
   try:
    r=c.post('/api/captura/',data,content_type='application/json')
    return r.status_code,r.json()
   finally:close_old_connections()
  with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(submit,clients))
  self.assertTrue(all(status in [200,201] for status,_ in results),results)
  self.assertEqual(Actividad.objects.count(),1)
  self.assertEqual({r['data']['codigo'] for _,r in results},{reservation['codigo']})
