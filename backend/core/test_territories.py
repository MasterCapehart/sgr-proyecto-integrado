import uuid
from django.test import TestCase
from .test_unified_capture import UnifiedCaptureTests
from .models import Rol, Actividad

class TerritoryTests(TestCase):
 setUp=UnifiedCaptureTests.setUp
 def send(self,path,data,method='post'):
  return getattr(self.client,method)(path,data,content_type='application/json')
 def create(self,name='Sector de prueba'):
  r=self.send('/api/territorios/',{'nombre':name,'descripcion':'Territorio ficticio'})
  self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_catalogo_codigo_delegacion_y_version(self):
  t=self.create();self.assertTrue(t['codigo'].startswith('TER-'));self.assertEqual(t['delegacion'],self.d.pk)
  r=self.send(f'/api/territorios/{t["id"]}/',{'_version':1,'nombre':'Nombre corregido'},'patch');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(r.json()['data']['codigo'],t['codigo'])
  self.assertEqual(self.send(f'/api/territorios/{t["id"]}/',{'_version':1,'nombre':'Viejo'},'patch').status_code,409)
 def test_aislamiento_y_permiso(self):
  t=self.create();session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save()
  self.assertEqual(self.client.get(f'/api/territorios/{t["id"]}/').status_code,404)
  self.u.is_superuser=False;self.u.rol=Rol.objects.create(nombre='Consulta territorial',permisos=['territorios.ver']);self.u.save()
  self.assertEqual(self.client.get('/api/territorios/').status_code,200)
  self.assertEqual(self.send('/api/territorios/',{'nombre':'Prohibido'}).status_code,403)
  self.client.logout();self.assertEqual(self.client.get('/api/territorios/').status_code,401)
 def test_rechaza_inyeccion_y_nombre_duplicado(self):
  self.create();self.assertEqual(self.send('/api/territorios/',{'nombre':' SECTOR DE PRUEBA '}).status_code,409)
  for extra in [{'delegacion':self.other_d.pk},{'codigo':'MANUAL'},{'activo':False}]:
   self.assertEqual(self.send('/api/territorios/',{'nombre':'Otro',**extra}).status_code,400)
 def test_vinculo_inactivo_y_texto_historico(self):
  t=self.create();payload=UnifiedCaptureTests.activity(self,territorio_catalogo=t['id']);payload['clave_idempotencia']=uuid.uuid4().hex
  r=self.send('/api/operacion/actividades/',payload);self.assertEqual(r.status_code,201,r.content)
  a=Actividad.objects.get();self.assertEqual(a.territorio_catalogo_id,t['id']);self.assertEqual(a.sector,'Sector QA')
  r=self.send(f'/api/territorios/{t["id"]}/estado/',{'_version':1,'activo':False,'motivo':'Cierre de prueba'});self.assertEqual(r.status_code,200,r.content)
  a.refresh_from_db();self.assertEqual(a.sector,'Sector QA');self.assertEqual(a.territorio_catalogo_id,t['id'])
  payload['clave_idempotencia']=uuid.uuid4().hex
  self.assertEqual(self.send('/api/operacion/actividades/',payload).status_code,400)
  self.assertEqual(self.send(f'/api/operacion/actividades/{a.pk}/',{'_version':a.version,'accion':'Corrección de texto'},'patch').status_code,200)
 def test_referencia_de_otra_delegacion(self):
  t=self.create();session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save()
  payload=UnifiedCaptureTests.activity(self,territorio_catalogo=t['id'])
  self.assertEqual(self.send('/api/operacion/actividades/',payload).status_code,400)

 def test_vecino_vinculado_y_delegacion_ajena(self):
  t=self.create();data=dict(nombre='Vecino ficticio territorial',telefono='912345678',sector='Texto original',territorio_catalogo=t['id'],clave_idempotencia=uuid.uuid4().hex)
  r=self.send('/api/vecinos/',data);self.assertEqual(r.status_code,201,r.content);v=r.json()['data'];self.assertEqual(v['territorio_catalogo'],t['id']);self.assertEqual(v['sector'],'Texto original')
  session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save();data['clave_idempotencia']=uuid.uuid4().hex
  self.assertEqual(self.send('/api/vecinos/',data).status_code,400)
 def test_organizacion_vinculada_y_rechazo_inactiva(self):
  t=self.create();data=dict(nombre='Junta ficticia territorial',tipo='Junta de vecinos',territorio='Referencia histórica',territorio_catalogo=t['id'],clave_idempotencia=uuid.uuid4().hex)
  r=self.send('/api/organizaciones/',data);self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['territorio_catalogo'],t['id'])
  self.assertEqual(self.send(f'/api/territorios/{t["id"]}/estado/',{'_version':1,'activo':False,'motivo':'Prueba'}).status_code,200)
  data['clave_idempotencia']=uuid.uuid4().hex;data['nombre']='Otra organización'
  self.assertEqual(self.send('/api/organizaciones/',data).status_code,400)
 def test_estado_exige_motivo_y_no_borra(self):
  t=self.create();self.assertEqual(self.send(f'/api/territorios/{t["id"]}/estado/',{'_version':1,'activo':False,'motivo':''}).status_code,400)
  self.assertEqual(self.client.delete(f'/api/territorios/{t["id"]}/').status_code,405)
  self.assertEqual(self.client.get(f'/api/territorios/{t["id"]}/').json()['data']['activo'],True)
