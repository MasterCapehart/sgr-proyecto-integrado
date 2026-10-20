from django.test import TestCase
from .models import Delegacion,Usuario,EventoLocal

class CodeReservationTests(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='ANTERIOR',nombre='Delegación QA')
  self.u=Usuario.objects.create_superuser('reserva_qa',password='LocalQA!937',delegacion=self.d);self.client.force_login(self.u)
 def post(self,url,data):return self.client.post('/api/'+url+'/',data,content_type='application/json')
 def reserve(self):
  r=self.post('delegaciones/reservar-codigo',{});self.assertEqual(r.status_code,200,r.content);return r.json()['data']
 def test_mismo_codigo_visible_y_guardado(self):
  reserved=self.reserve();self.assertTrue(reserved['codigo'].startswith('DEL-'))
  r=self.post('delegaciones',{'nombre':'Nueva','direccion':'QA','comuna':'La Serena','_reserva_codigo':reserved['reserva']});self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['codigo'],reserved['codigo'])
  self.assertEqual(self.post('delegaciones',{'nombre':'Otra','_reserva_codigo':reserved['reserva']}).status_code,400)
 def test_cancelar_reserva_no_crea_delegacion_y_numeros_no_se_reutilizan(self):
  a=self.reserve();b=self.reserve();self.assertNotEqual(a['codigo'],b['codigo']);self.assertEqual(Delegacion.objects.count(),1)
 def test_no_admite_reserva_de_otro_usuario_recurso_o_firma(self):
  a=self.reserve()
  self.assertEqual(self.post('cargos',{'nombre':'Cargo','area':'QA','_reserva_codigo':a['reserva']}).status_code,400)
  self.assertEqual(self.post('delegaciones',{'nombre':'Otra','_reserva_codigo':a['reserva']+'X'}).status_code,400)
  other=Usuario.objects.create_superuser('otra_reserva',password='LocalQA!937',delegacion=self.d);self.client.force_login(other)
  self.assertEqual(self.post('delegaciones',{'nombre':'Otra','_reserva_codigo':a['reserva']}).status_code,400)
 def test_reserva_sin_permiso_o_sesion_rechazada(self):
  self.client.logout();self.assertEqual(self.post('delegaciones/reservar-codigo',{}).status_code,401)
  u=Usuario.objects.create_user('sin_permiso_reserva',delegacion=self.d);self.client.force_login(u)
  self.assertEqual(self.post('delegaciones/reservar-codigo',{}).status_code,403)
 def test_fallo_validacion_permita_corregir_y_guardar_misma_reserva(self):
  a=self.reserve();self.assertEqual(self.post('delegaciones',{'_reserva_codigo':a['reserva']}).status_code,400)
  r=self.post('delegaciones',{'nombre':'Corregida','direccion':'QA','comuna':'La Serena','_reserva_codigo':a['reserva']});self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['codigo'],a['codigo'])

 def test_reserva_con_formato_invalido_no_produce_error_interno(self):
  for value in [{},[],23,False]:
   self.assertEqual(self.post('delegaciones',{'nombre':'Inválida','_reserva_codigo':value}).status_code,400)
