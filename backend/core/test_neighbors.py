import uuid
from django.apps import apps
from django.test import TestCase
from . import test_capture_form as helpers
from .models import Actividad,Rol

class NeighborTests(TestCase):
 setUp=helpers.CaptureFormTests.setUp
 activity=helpers.CaptureFormTests.activity
 payload=helpers.CaptureFormTests.payload
 post_capture=helpers.CaptureFormTests.post
 def data(self,**extra):return {**dict(nombre='Persona ficticia vecinal',rut='12.345.678-5',telefono='912345678',sector='Sector QA',junta_vecinos='JJVV QA',clave_idempotencia=uuid.uuid4().hex),**extra}
 def post(self,data):return self.client.post('/api/vecinos/',data,content_type='application/json')
 def search(self,q):return self.client.post('/api/vecinos/buscar/',{'q':q},content_type='application/json')
 def test_registrar_buscar_y_reutilizar_datos(self):
  r=self.post(self.data());self.assertEqual(r.status_code,201,r.content);v=r.json()['data'];self.assertEqual(v['rut'],'12345678-5')
  for q in ['ficticia','12.345.678-5']:
   response=self.search(q);self.assertEqual(response.status_code,200,response.content);self.assertEqual(response.json()['results'][0]['id'],v['id'])
  data=self.payload(vecino=v['id']);data['actividad']['contacto']=v['nombre'];data['actividad']['rut_contacto']=v['rut']
  r=self.post_capture(data);self.assertEqual(r.status_code,201,r.content);a=Actividad.objects.get();self.assertEqual(a.vecino_id,v['id']);self.assertEqual(a.rut_contacto,v['rut']);self.assertEqual(self.post_capture(data).status_code,200)
 def test_no_duplica_run_normalizado_ni_reintento(self):
  data=self.data();r=self.post(data);self.assertEqual(r.status_code,201,r.content)
  self.assertEqual(self.post(data).status_code,200)
  self.assertEqual(self.post(self.data(rut='12345678-5')).status_code,409)
  data['nombre']='Otra persona';self.assertEqual(self.post(data).status_code,409)
 def test_nombre_y_run_de_otro_contexto_no_se_exponen(self):
  r=self.post(self.data());self.assertEqual(r.status_code,201,r.content);v=r.json()['data']
  session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save()
  self.assertEqual(self.search('ficticia').json()['results'],[])
  self.assertEqual(self.post_capture(self.payload(vecino=v['id'])).status_code,404)
  self.assertEqual(self.post(self.data()).status_code,201)
 def test_sin_permiso_o_sesion_no_consulta_ni_crea(self):
  self.u.is_superuser=False;self.u.rol=Rol.objects.create(nombre='Vecinal consulta QA',permisos=['actividades.ver']);self.u.save()
  self.assertEqual(self.search('ficticia').status_code,403);self.assertEqual(self.post(self.data()).status_code,403)
  self.client.logout();self.assertEqual(self.search('ficticia').status_code,401)
 def test_run_invalido_y_campos_inyectados_rechazados(self):
  self.assertEqual(self.post(self.data(rut='12345678-9')).status_code,400)
  self.assertEqual(self.post(self.data(delegacion=self.other_d.pk)).status_code,400)
  self.assertEqual(self.post(self.data(nombre=True)).status_code,400)
 def test_busqueda_vacia_no_lista_todo_y_nombre_sin_run_permitido(self):
  r=self.post(self.data(rut=''));self.assertEqual(r.status_code,201,r.content)
  self.assertEqual(self.search('').json()['results'],[]);self.assertEqual(self.search('pe').json()['results'],[])
 def test_vecino_no_puede_atribuirse_a_otro_nombre(self):
  r=self.post(self.data());self.assertEqual(r.status_code,201,r.content)
  data=self.payload(vecino=r.json()['data']['id']);self.assertEqual(self.post_capture(data).status_code,400);self.assertFalse(Actividad.objects.exists())
 def test_cambiar_telefono_snapshot_no_cambia_padron(self):
  r=self.post(self.data());self.assertEqual(r.status_code,201,r.content);v=r.json()['data'];data=self.payload(vecino=v['id']);data['actividad'].update(contacto=v['nombre'],telefono='987654321')
  response=self.post_capture(data);self.assertEqual(response.status_code,201,response.content)
  self.assertEqual(self.search(v['rut']).json()['results'][0]['telefono'],'912345678');self.assertEqual(Actividad.objects.get().telefono,'987654321')
 def test_run_con_cero_inicial_no_crea_otro_vecino(self):
  r=self.post(self.data(rut='1234567-4'));self.assertEqual(r.status_code,201,r.content)
  self.assertEqual(self.post(self.data(rut='01234567-4')).status_code,409)
 def test_busqueda_tiene_limite_y_captura_valida_run_social(self):
  r=self.post(self.data());self.assertEqual(r.status_code,201,r.content);v=r.json()['data']
  data=self.payload(vecino=v['id'],social=dict(tipo_atencion=self.t.pk,sub_atencion=self.s.pk,rut_solicitante='1234567-4'))
  data['actividad'].update(contacto=v['nombre'],rut_contacto=v['rut'])
  self.assertEqual(self.post_capture(data).status_code,400);self.assertFalse(Actividad.objects.exists())
  Model=apps.get_model('core','Vecino')
  Model.objects.bulk_create([Model(nombre='Persona límite '+str(i),delegacion=self.d,creado_por=self.u,clave_idempotencia=uuid.uuid4().hex,captura_hash='x') for i in range(21)])
  r=self.search('Persona límite');self.assertEqual(len(r.json()['results']),20);self.assertTrue(r.json()['has_more'])
 def test_editar_actividad_no_cambia_identidad_del_vecino(self):
  v=self.post(self.data()).json()['data'];data=self.payload(vecino=v['id']);data['actividad'].update(contacto=v['nombre'],rut_contacto=v['rut']);created=self.post_capture(data);self.assertEqual(created.status_code,201,created.content)
  a=created.json()['data'];r=self.client.patch('/api/operacion/actividades/'+str(a['id'])+'/',{'_version':a['version'],'contacto':'Otra persona','rut_contacto':'1234567-4'},content_type='application/json');self.assertEqual(r.status_code,400,r.content)
  self.assertEqual(Actividad.objects.get().contacto,v['nombre'])
 def test_reintento_que_confirma_entre_consultas_se_recupera(self):
  from unittest.mock import patch
  from . import neighbors
  data=self.data();r=self.post(data);self.assertEqual(r.status_code,201,r.content)
  original=neighbors.prior;calls=0
  def visible_after_first(*args):
   nonlocal calls
   calls+=1
   return None if calls==1 else original(*args)
  with patch.object(neighbors,'prior',side_effect=visible_after_first):
   r=self.post(data);self.assertEqual(r.status_code,200,r.content)
