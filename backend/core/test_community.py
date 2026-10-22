import uuid
from django.test import TestCase
from . import test_neighbors as neighbor_helpers
from .models import Rol

class CommunityTests(TestCase):
 setUp=neighbor_helpers.NeighborTests.setUp
 def send(self,url,data,method='post'):return getattr(self.client,method)(url,data,content_type='application/json')
 def neighbor(self):
  r=self.send('/api/vecinos/',dict(nombre='Vecino comunitario ficticio',telefono='912345678',sector='Sector QA',clave_idempotencia=uuid.uuid4().hex));self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def org(self,name='Junta ficticia'):
  r=self.send('/api/organizaciones/',dict(nombre=name,tipo='Junta de vecinos',territorio='Sector QA',clave_idempotencia=uuid.uuid4().hex));self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_organizacion_socios_desconocidos_y_cero(self):
  o=self.org();self.assertIsNone(o['socios_activos']);self.assertEqual(o['delegacion'],self.d.pk)
  r=self.send(f'/api/organizaciones/{o["id"]}/',dict(_version=o['version'],socios_activos=0),'patch');self.assertEqual(r.status_code,200,r.content);self.assertEqual(r.json()['data']['socios_activos'],0)
 def test_vecino_edicion_conflicto_y_snapshot(self):
  v=self.neighbor();r=self.send(f'/api/vecinos/{v["id"]}/',dict(_version=v['version'],direccion='Dirección ficticia'),'patch');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(self.send(f'/api/vecinos/{v["id"]}/',dict(_version=v['version'],nombre='Cambio'),'patch').status_code,409)
 def test_pertenencia_multiple_con_roles_y_duplicados(self):
  v=self.neighbor();a=self.org();b=self.org('Club ficticio')
  for org,role in [(a,'Dirigente'),(b,'Integrante')]:
   data=dict(vecino=v['id'],organizacion=org['id'],rol=role)
   r=self.send('/api/pertenencias/',data);self.assertEqual(r.status_code,201,r.content);self.assertEqual(self.send('/api/pertenencias/',data).status_code,409)
  detail=self.client.get(f'/api/vecinos/{v["id"]}/').json()['data'];self.assertEqual(len(detail['pertenencias']),2)
 def test_desactivar_vecino_lo_retira_de_busqueda(self):
  v=self.neighbor();r=self.send(f'/api/vecinos/{v["id"]}/estado/',dict(_version=v['version'],activo=False,motivo='Ensayo de desactivación'));self.assertEqual(r.status_code,200,r.content)
  r=self.send('/api/vecinos/buscar/',{'q':'comunitario'});self.assertEqual(r.json()['results'],[])
  self.assertEqual(self.client.get(f'/api/vecinos/{v["id"]}/').status_code,200)
 def test_funcionario_edita_vecino_no_desactiva_ni_crea_organizacion(self):
  v=self.neighbor();self.u.is_superuser=False;self.u.rol=Rol.objects.create(nombre='Funcionario QA comunidad',permisos=['vecinos.ver','vecinos.crear','vecinos.editar','organizaciones.ver','pertenencias.ver']);self.u.save()
  self.assertEqual(self.client.get('/api/vecinos/directorio/').status_code,200)
  self.assertEqual(self.send(f'/api/vecinos/{v["id"]}/',dict(_version=v['version'],direccion='Dirección'),'patch').status_code,200)
  self.assertEqual(self.send(f'/api/vecinos/{v["id"]}/estado/',dict(_version=2,activo=False,motivo='QA')).status_code,403)
  self.assertEqual(self.send('/api/organizaciones/',dict(nombre='No autorizado')).status_code,403)
 def test_aislamiento_delegacion_y_referencias(self):
  v=self.neighbor();o=self.org();session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save()
  self.assertEqual(self.client.get(f'/api/vecinos/{v["id"]}/').status_code,404)
  self.assertEqual(self.client.get(f'/api/organizaciones/{o["id"]}/').status_code,404)
  self.assertEqual(self.send('/api/pertenencias/',dict(vecino=v['id'],organizacion=o['id'],rol='Dirigente')).status_code,404)
 def test_inactivo_no_admite_pertenencia_nueva_y_historial_se_conserva(self):
  v=self.neighbor();o=self.org();r=self.send('/api/pertenencias/',dict(vecino=v['id'],organizacion=o['id'],rol='Dirigente'));self.assertEqual(r.status_code,201,r.content)
  self.assertEqual(self.send(f'/api/organizaciones/{o["id"]}/estado/',dict(_version=o['version'],activo=False,motivo='QA')).status_code,200)
  detail=self.client.get(f'/api/vecinos/{v["id"]}/').json()['data'];self.assertFalse(detail['pertenencias'][0]['organizacion_activa'])
  self.assertEqual(self.send('/api/pertenencias/',dict(vecino=v['id'],organizacion=o['id'],rol='Integrante')).status_code,400)
 def test_validaciones_y_campos_inyectados(self):
  for extra in [dict(socios_activos=-1),dict(delegacion=self.other_d.pk)]:
   data=dict(nombre='Org ficticia',tipo='Junta de vecinos',territorio='QA',clave_idempotencia=uuid.uuid4().hex);data.update(extra)
   self.assertEqual(self.send('/api/organizaciones/',data).status_code,400)
 def test_renombrar_vecino_no_rompe_edicion_de_actividad_historica(self):
  v=self.neighbor();data=dict(clave_idempotencia=uuid.uuid4().hex,vecino=v['id'],actividad=neighbor_helpers.NeighborTests.activity(self,contacto=v['nombre']))
  r=self.send('/api/captura/',data);self.assertEqual(r.status_code,201,r.content);a=r.json()['data']
  r=self.send(f'/api/vecinos/{v["id"]}/',dict(_version=v['version'],nombre='Nombre actualizado del directorio'),'patch');self.assertEqual(r.status_code,200,r.content)
  r=self.send(f'/api/operacion/actividades/{a["id"]}/',dict(_version=a['version'],accion='Seguimiento histórico'),'patch');self.assertEqual(r.status_code,200,r.content);self.assertEqual(r.json()['data']['contacto'],v['nombre'])
 def test_reactivar_pertenencia_no_duplica_y_estado_exige_motivo(self):
  v=self.neighbor();o=self.org();link=self.send('/api/pertenencias/',dict(vecino=v['id'],organizacion=o['id'],rol='Integrante')).json()['data']
  self.assertEqual(self.send(f'/api/pertenencias/{link["id"]}/estado/',dict(_version=link['version'],activo=False,motivo='')).status_code,400)
  r=self.send(f'/api/pertenencias/{link["id"]}/estado/',dict(_version=link['version'],activo=False,motivo='Fin de participación'));self.assertEqual(r.status_code,200)
  data=r.json()['data'];r=self.send(f'/api/pertenencias/{link["id"]}/estado/',dict(_version=data['version'],activo=True,motivo='Retoma participación'));self.assertEqual(r.status_code,200)
  self.assertEqual(len(self.client.get(f'/api/vecinos/{v["id"]}/').json()['data']['pertenencias']),1)
 def test_reintento_organizacion_y_fechas_invalidas(self):
  data=dict(nombre='Club',tipo='Organización comunitaria',territorio='QA',clave_idempotencia=uuid.uuid4().hex)
  first=self.send('/api/organizaciones/',data);self.assertEqual(first.status_code,201,first.content);repeat=self.send('/api/organizaciones/',data);self.assertEqual(repeat.status_code,200,repeat.content);self.assertEqual(first.json()['data']['id'],repeat.json()['data']['id'])
  data['nombre']='Otro';self.assertEqual(self.send('/api/organizaciones/',data).status_code,409)
  data['clave_idempotencia']=uuid.uuid4().hex;data['fecha_constitucion']='no es fecha';self.assertEqual(self.send('/api/organizaciones/',data).status_code,400)
