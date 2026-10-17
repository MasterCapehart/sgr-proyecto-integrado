from django.test import TestCase, Client
from .models import Usuario, TipoAtencion, Delegacion, EventoLocal

class RevisionEntrega(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='REV',nombre='Delegación revisión')
  self.u=Usuario.objects.create_superuser('revision','revision@example.test','ClaveRevision!983',delegacion=self.d)
  self.client.force_login(self.u)
  self.tipo=TipoAtencion.objects.create(codigo='REV',nombre='Tipo revisión')
 def test_actualizacion_exige_version(self):
  self.assertEqual(self.client.patch(f'/api/tipos-atencion/{self.tipo.pk}/',{'nombre':'Cambio'},content_type='application/json').status_code,428)
 def test_conflicto_no_sobrescribe(self):
  url=f'/api/tipos-atencion/{self.tipo.pk}/';version=self.client.get(url).json()['data'].get('version')
  r=self.client.patch(url,{'nombre':'Primer cambio','_version':version},content_type='application/json');self.assertEqual(r.status_code,200,r.content)
  r=self.client.patch(url,{'nombre':'Cambio obsoleto','_version':version},content_type='application/json');self.assertEqual(r.status_code,409,r.content)
  self.tipo.refresh_from_db();self.assertEqual(self.tipo.nombre,'Primer cambio')
 def test_auditoria_antes_despues_sin_secretos(self):
  url=f'/api/tipos-atencion/{self.tipo.pk}/';version=self.client.get(url).json()['data'].get('version')
  self.client.patch(url,{'nombre':'Cambio auditado','_version':version},content_type='application/json')
  r=self.client.get('/api/auditoria/');self.assertEqual(r.status_code,200,r.content)
  record=r.json()['results'][0];self.assertEqual(record['antes']['nombre'],'Tipo revisión');self.assertEqual(record['despues']['nombre'],'Cambio auditado')
 def test_auditoria_no_modificable(self):
  self.assertEqual(self.client.post('/api/auditoria/',{},content_type='application/json').status_code,405)
 def test_auditoria_sin_permiso_y_fuera_del_ambito(self):
  from .models import Rol
  role=Rol.objects.create(nombre='Consulta revisión',permisos=['tipos-atencion.ver'])
  user=Usuario.objects.create_user('consulta_revision',email='consulta_revision@example.test',rol=role,delegacion=self.d)
  self.client.force_login(user);self.assertEqual(self.client.get('/api/auditoria/').status_code,403)
  role.permisos=['auditoria.ver'];role.save()
  other=Delegacion.objects.create(codigo='OTRA',nombre='Otra delegación revisión')
  EventoLocal.objects.create(usuario=self.u,recurso='usuarios',accion='editar',delegacion=other,antes={'email':'no-visible@example.test'})
  self.assertEqual(self.client.get('/api/auditoria/').json()['count'],0)
 def test_usuario_auditado_no_conserva_clave(self):
  from .models import Rol
  role=Rol.objects.create(nombre='Rol revisión',permisos=['tipos-atencion.ver'])
  payload={'username':'nuevo_revision','email':'nuevo_revision@example.test','first_name':'Persona','rol':role.pk,'delegacion':self.d.pk,'delegaciones':[self.d.pk],'password':'ClavePrivada!8473'}
  response=self.client.post('/api/usuarios/',payload,content_type='application/json');self.assertEqual(response.status_code,201,response.content)
  event=EventoLocal.objects.get(recurso='usuarios',accion='crear');self.assertNotIn('password',event.despues);self.assertNotIn('ClavePrivada',str(event.despues))
 def test_panel_tecnico_no_elude_version_y_auditoria(self):
  self.assertEqual(self.client.post(f'/admin/core/tipoatencion/{self.tipo.pk}/change/',{'codigo':'REV','nombre':'BYPASS','estado':'on'}).status_code,403)
 def test_credenciales_con_tipo_json_invalido_no_generan_error_500(self):
  self.assertEqual(self.client.post('/api/login/',{'username':'revision','password':{'dato':'incorrecto'}},content_type='application/json').status_code,400)
 def test_password_usuario_debe_ser_texto(self):
  from .models import Rol
  self.u.first_name='Persona';self.u.rol=Rol.objects.create(nombre='Rol formato',permisos=['tipos-atencion.ver']);self.u.save();self.u.delegaciones.add(self.d)
  version=self.client.get(f'/api/usuarios/{self.u.pk}/').json()['data']['version']
  self.assertEqual(self.client.patch(f'/api/usuarios/{self.u.pk}/',{'password':['incorrecto'],'_version':version},content_type='application/json').status_code,400)
 def test_no_reactiva_subatencion_de_tipo_inactivo(self):
  from .models import SubAtencion
  self.tipo.estado=False;self.tipo.save()
  sub=SubAtencion.objects.create(codigo='REV-S',nombre='Sub revisión',tipo_atencion=self.tipo,estado=False)
  response=self.client.post(f'/api/subatenciones/{sub.pk}/toggle-estado/',{'_version':sub.version},content_type='application/json')
  self.assertEqual(response.status_code,400,response.content)
