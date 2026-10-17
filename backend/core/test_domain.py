from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Usuario, Delegacion, ItemMeta, Rol

class OperacionDominio(TestCase):
 @classmethod
 def setUpClass(cls):
  import tempfile
  from django.test import override_settings
  cls.media=tempfile.TemporaryDirectory(prefix='sgr-domain-tests-')
  cls.settings_override=override_settings(MEDIA_ROOT=cls.media.name);cls.settings_override.enable()
  super().setUpClass()
 @classmethod
 def tearDownClass(cls):
  super().tearDownClass();cls.settings_override.disable();cls.media.cleanup()

 def setUp(self):
  self.d=Delegacion.objects.create(codigo='DOM',nombre='Dominio')
  self.u=Usuario.objects.create_superuser('dominio','dominio@example.test','ClaveDominio!983',delegacion=self.d)
  self.client.force_login(self.u)
  self.item=ItemMeta.objects.create(codigo='DOM',nombre='Ítem dominio')
 def activity(self):
  r=self.client.post('/api/operacion/actividades/',{'fecha':'2026-10-15','solicitud':'Necesidad ciudadana','accion':'Visita de terreno','contacto':'Contacto','telefono':'+56912345678','sector':'Centro','item':self.item.pk},content_type='application/json')
  self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_actividad_codigo_inmutable_y_conflicto(self):
  a=self.activity();url=f"/api/operacion/actividades/{a['id']}/"
  r=self.client.patch(url,{'_version':a['version'],'accion':'Seguimiento'},content_type='application/json');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(r.json()['data']['codigo'],a['codigo'])
  self.assertEqual(self.client.patch(url,{'_version':a['version'],'accion':'Obsoleto'},content_type='application/json').status_code,409)
 def test_aislamiento_actividad(self):
  a=self.activity();other=Delegacion.objects.create(codigo='DOM2',nombre='Otra dominio')
  role=Rol.objects.create(nombre='Lector dominio',permisos=['actividades.ver'])
  u=Usuario.objects.create_user('lector_dom',rol=role,delegacion=other);self.client.force_login(u)
  self.assertEqual(self.client.get('/api/operacion/actividades/').json()['count'],0)
  self.assertEqual(self.client.get(f"/api/operacion/actividades/{a['id']}/").status_code,404)
 def test_evidencia_privada_y_no_autoaprobacion(self):
  a=self.activity()
  r=self.client.post('/api/operacion/evidencias/',{'actividad':a['id'],'descripcion':'Respaldo','archivo':SimpleUploadedFile('respaldo.pdf',b'%PDF-1.4\n%%EOF',content_type='application/pdf')})
  self.assertEqual(r.status_code,201,r.content);e=r.json()['data']
  self.assertEqual(self.client.get(f"/api/operacion/evidencias/{e['id']}/archivo/").status_code,200)
  r=self.client.post(f"/api/operacion/evidencias/{e['id']}/revisar/",{'_version':e['version'],'decision':'Aprobada','observacion':'Revisada'},content_type='application/json');self.assertEqual(r.status_code,400,r.content)
 def test_archivo_no_permitido(self):
  a=self.activity();r=self.client.post('/api/operacion/evidencias/',{'actividad':a['id'],'descripcion':'No seguro','archivo':SimpleUploadedFile('pagina.html',b'<html>contenido</html>')});self.assertEqual(r.status_code,400)
 def test_compromiso_y_mensaje_reales(self):
  r=self.client.post('/api/operacion/compromisos/',{'descripcion':'Resolver solicitud','solicitante':'Vecina','sector':'Centro','responsable':self.u.pk,'fecha_comprometida':'2026-11-01','area_apoyo':'Operaciones','origen':'Interno'},content_type='application/json');self.assertEqual(r.status_code,201,r.content)
  c=r.json()['data'];url=f"/api/operacion/compromisos/{c['id']}/mensajes/"
  self.assertEqual(self.client.post(url,{'contenido':'Primer seguimiento'},content_type='application/json').status_code,201)
  self.assertEqual(self.client.get(url).json()['results'][0]['contenido'],'Primer seguimiento')
 def evidence(self,a):
  r=self.client.post('/api/operacion/evidencias/',{'actividad':a['id'],'descripcion':'Respaldo','archivo':SimpleUploadedFile('respaldo.pdf',b'%PDF-1.4\n%%EOF',content_type='application/pdf')});self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def verifier(self):
  role=Rol.objects.create(nombre='Revisor dominio',permisos=['actividades.ver','actividades.ver_equipo','evidencias.ver','evidencias.revisar','conversaciones.crear'])
  return Usuario.objects.create_user('revisor_dom',rol=role,delegacion=self.d)
 def test_revisor_ajeno_aprueba_y_audita(self):
  a=self.activity();e=self.evidence(a);self.client.force_login(self.verifier());r=self.client.post(f"/api/operacion/evidencias/{e['id']}/revisar/",{'_version':e['version'],'decision':'Aprobada','observacion':'Conforme'},content_type='application/json');self.assertEqual(r.status_code,200,r.content)
  from .models import Actividad, EventoLocal
  self.assertEqual(Actividad.objects.get(pk=a['id']).estado,'Validada');self.assertTrue(EventoLocal.objects.filter(recurso='evidencias',accion='revisar').exists())
 def test_descarga_no_autorizada(self):
  a=self.activity();e=self.evidence(a);other=Delegacion.objects.create(codigo='OTH',nombre='Otra archivo');role=Rol.objects.create(nombre='Archivos otra',permisos=['evidencias.ver','evidencias.ver_equipo']);u=Usuario.objects.create_user('otro_archivo',rol=role,delegacion=other);self.client.force_login(u)
  self.assertEqual(self.client.get(e['archivo_url']).status_code,404)
 def test_rechazo_y_reemplazo_conservan_historial(self):
  a=self.activity();e=self.evidence(a);self.client.force_login(self.verifier());r=self.client.post(f"/api/operacion/evidencias/{e['id']}/revisar/",{'_version':e['version'],'decision':'Corrección','observacion':'Adjuntar respaldo completo'},content_type='application/json');self.assertEqual(r.status_code,200,r.content)
  self.client.force_login(self.u);r=self.client.post('/api/operacion/evidencias/',{'actividad':a['id'],'reemplaza':e['id'],'descripcion':'Corregido','archivo':SimpleUploadedFile('nuevo.pdf',b'%PDF-1.4\n%%EOF',content_type='application/pdf')});self.assertEqual(r.status_code,201,r.content)
  old=self.client.get(f"/api/operacion/evidencias/{e['id']}/").json()['data'];self.assertFalse(old['vigente']);self.assertEqual(len(old['revisiones']),1)
 def test_fecha_futura_y_codigo_no_modificable(self):
  a=self.activity();r=self.client.patch(f"/api/operacion/actividades/{a['id']}/",{'_version':a['version'],'codigo':'inventado'},content_type='application/json');self.assertEqual(r.status_code,400)
  r=self.client.patch(f"/api/operacion/actividades/{a['id']}/",{'_version':a['version'],'fecha':'2099-01-01'},content_type='application/json');self.assertEqual(r.status_code,400)
 def test_comentario_fuera_del_ambito(self):
  a=self.activity();other=Delegacion.objects.create(codigo='OUT',nombre='Otra mensaje');role=Rol.objects.create(nombre='Comentar otra',permisos=['actividades.ver','conversaciones.crear']);u=Usuario.objects.create_user('otro_mensaje',rol=role,delegacion=other);self.client.force_login(u)
  self.assertEqual(self.client.post(f"/api/operacion/actividades/{a['id']}/mensajes/",{'contenido':'No autorizado'},content_type='application/json').status_code,404)
 def test_campos_obligatorios_y_permiso(self):
  self.assertEqual(self.client.post('/api/operacion/compromisos/',{},content_type='application/json').status_code,400)
  role=Rol.objects.create(nombre='Solo leer dominio',permisos=['actividades.ver']);u=Usuario.objects.create_user('solo_dom',rol=role,delegacion=self.d);self.client.force_login(u)
  self.assertEqual(self.client.post('/api/operacion/actividades/',{},content_type='application/json').status_code,403)
 def test_excel_real_y_filtros(self):
  a=self.activity();r=self.client.get('/api/operacion/actividades/export/?search='+a['codigo']);self.assertEqual(r.status_code,200)
  from openpyxl import load_workbook
  from io import BytesIO
  book=load_workbook(BytesIO(r.content));self.assertIn(a['codigo'],str(list(book.active.values)))
 def test_sin_sesion_no_hay_operacion(self):
  self.client.logout();self.assertEqual(self.client.get('/api/operacion/actividades/').status_code,401);self.assertEqual(self.client.get('/api/operacion/opciones/').status_code,401)
 def test_lectura_de_equipo_no_concede_edicion(self):
  a=self.activity();role=Rol.objects.create(nombre='Leer equipo dominio',permisos=['actividades.ver','actividades.ver_equipo','actividades.editar']);u=Usuario.objects.create_user('equipo_dom',rol=role,delegacion=self.d);self.client.force_login(u)
  self.assertEqual(self.client.get(f"/api/operacion/actividades/{a['id']}/").status_code,200)
  self.assertEqual(self.client.patch(f"/api/operacion/actividades/{a['id']}/",{'_version':a['version'],'accion':'No permitido'},content_type='application/json').status_code,403)
 def test_observacion_no_textual_devuelve_400_sin_cambiar_compromiso(self):
  from .models import Compromiso
  c=Compromiso.objects.create(delegacion=self.d,autor=self.u,responsable=self.u,descripcion='Prueba',solicitante='Vecina',sector='Centro',fecha_comprometida='2026-11-01',area_apoyo='Operaciones',origen='Interno')
  self.client.raise_request_exception=False
  for value in [None,123,[]]:
   r=self.client.patch(f'/api/operacion/compromisos/{c.pk}/',{'_version':1,'estado':'En proceso','observacion':value},content_type='application/json');self.assertEqual(r.status_code,400,r.content[:200]);c.refresh_from_db();self.assertEqual(c.estado,'Ingresado');self.assertEqual(c.version,1)
