from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Usuario, Rol, Delegacion, TipoAtencion, SubAtencion, ItemMeta, Atencion

class CierreLocal(TestCase):
 @classmethod
 def setUpClass(cls):
  import tempfile
  from django.test import override_settings
  cls.media=tempfile.TemporaryDirectory(prefix='sgr-cierre-');cls.override=override_settings(MEDIA_ROOT=cls.media.name);cls.override.enable();super().setUpClass()
 @classmethod
 def tearDownClass(cls):
  super().tearDownClass();cls.override.disable();cls.media.cleanup()
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='CI',nombre='Cierre prueba')
  self.u=Usuario.objects.create_superuser('cierre','cierre@example.test','ClaveCierre!839',delegacion=self.d);self.client.force_login(self.u)
  self.tipo=TipoAtencion.objects.create(codigo='CI',nombre='Tipo original');self.sub=SubAtencion.objects.create(codigo='CI',nombre='Sub original',tipo_atencion=self.tipo);self.item=ItemMeta.objects.create(codigo='CI',nombre='Ítem original')
 def post(self,url,data):return self.client.post(url,data,content_type='application/json')
 def activity(self):
  r=self.post('/api/operacion/actividades/',{'fecha':str(timezone.localdate()),'solicitud':'Solicitud','accion':'Acción','contacto':'Vecino','telefono':'+56912345678','sector':'Centro','item':self.item.pk});self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def commitment(self):
  r=self.post('/api/operacion/compromisos/',{'fecha_solicitud':str(timezone.localdate()-timedelta(days=5)),'descripcion':'Compromiso vencido','solicitante':'Vecino','sector':'Centro','responsable':self.u.pk,'fecha_comprometida':str(timezone.localdate()-timedelta(days=2)),'area_apoyo':'Área','origen':'Interno'});self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_etiquetas_atencion_no_cambian_con_catalogo(self):
  r=self.post('/api/atenciones/',{'solicitante':'Persona','tipo_atencion':self.tipo.pk,'sub_atencion':self.sub.pk,'descripcion':'Prueba'});self.assertEqual(r.status_code,201,r.content);a=r.json()['data']
  r=self.client.patch(f'/api/tipos-atencion/{self.tipo.pk}/',{'_version':1,'nombre':'Tipo renombrado'},content_type='application/json');self.assertEqual(r.status_code,200,r.content)
  saved=self.client.get(f"/api/atenciones/{a['id']}/").json()['data'];self.assertEqual(saved['tipo_nombre'],'Tipo original');self.assertEqual(saved['catalogos_snapshot']['tipo_atencion']['version'],1)
 def test_etiqueta_actividad_y_cargos_historicos(self):
  a=self.activity();self.client.patch(f'/api/items-metas/{self.item.pk}/',{'_version':1,'nombre':'Ítem nuevo'},content_type='application/json')
  saved=self.client.get(f"/api/operacion/actividades/{a['id']}/").json()['data'];self.assertEqual(saved['item_nombre'],'Ítem original')
 def test_historial_de_catalogo_antes_y_despues(self):
  self.client.patch(f'/api/tipos-atencion/{self.tipo.pk}/',{'_version':1,'nombre':'Tipo nuevo'},content_type='application/json')
  r=self.client.get(f'/api/tipos-atencion/{self.tipo.pk}/historial/');self.assertEqual(r.status_code,200,r.content);self.assertEqual([x['version'] for x in r.json()['results']],[2,1])
 def test_cierre_conserva_atraso_y_bloquea_retroceso(self):
  c=self.commitment();url=f"/api/operacion/compromisos/{c['id']}/"
  r=self.client.patch(url,{'_version':c['version'],'estado':'Realizado','observacion':'Solución entregada'},content_type='application/json');self.assertEqual(r.status_code,200,r.content);c=r.json()['data'];self.assertEqual(c['dias_atraso_cierre'],2)
  r=self.client.patch(url,{'_version':c['version'],'estado':'Ingresado','observacion':'Retroceso'},content_type='application/json');self.assertEqual(r.status_code,400,r.content)
 def test_alerta_revisada_conserva_evento_y_ambito(self):
  c=self.commitment();r=self.client.get('/api/alertas/');self.assertEqual(r.status_code,200,r.content);a=next(x for x in r.json()['results'] if x['registro']==c['id'] and x['tipo']=='vencimiento')
  self.assertIn(str(c['id']),a['enlace']);self.assertTrue(a['motivo']);r=self.post(f"/api/alertas/{a['id']}/revisar/",{'_version':a['version']});self.assertEqual(r.status_code,200,r.content)
  all_events=self.client.get('/api/alertas/').json()['results'];self.assertEqual(len([x for x in all_events if x['id']==a['id']]),1);self.assertTrue(next(x for x in all_events if x['id']==a['id'])['revisada'])
  other=Delegacion.objects.create(codigo='CI2',nombre='Otra cierre');self.u.delegacion=other;self.u.save();self.client.force_login(self.u);self.assertEqual(self.client.get('/api/alertas/').json()['count'],0)
 def test_anulacion_auditable_no_borra_archivo(self):
  a=self.activity();r=self.client.post('/api/operacion/evidencias/',{'actividad':a['id'],'descripcion':'Respaldo','archivo':SimpleUploadedFile('respaldo.pdf',b'%PDF-1.4\n%%EOF',content_type='application/pdf')});self.assertEqual(r.status_code,201,r.content);e=r.json()['data']
  r=self.post(f"/api/operacion/evidencias/{e['id']}/anular/",{'_version':e['version'],'motivo':'Archivo no corresponde'});self.assertEqual(r.status_code,200,r.content);self.assertEqual(r.json()['data']['estado'],'Anulada')
  self.assertEqual(self.client.get(e['archivo_url']).status_code,200);self.assertEqual(self.client.get(f"/api/operacion/actividades/{a['id']}/").json()['data']['estado'],'Corrección')
 def test_politica_no_se_autoaprueba(self):
  r=self.client.get('/api/gobierno/');self.assertEqual(r.status_code,200,r.content);self.assertFalse(r.json()['data']['politica']['validada'])
 def test_consulta_no_anula_ni_configura_reglas(self):
  role=Rol.objects.create(nombre='Consulta cierre',permisos=['evidencias.ver','alertas.ver']);user=Usuario.objects.create_user('consulta_cierre',rol=role,delegacion=self.d);self.client.force_login(user)
  self.assertEqual(self.post('/api/operacion/evidencias/1/anular/',{'_version':1,'motivo':'Prueba'}).status_code,403);self.assertEqual(self.client.get('/api/gobierno/').status_code,403)
 def test_anulacion_exige_motivo_y_version_y_conserva_revision(self):
  from .models import RevisionEvidencia
  a=self.activity();e=self.client.post('/api/operacion/evidencias/',{'actividad':a['id'],'descripcion':'Respaldo','archivo':SimpleUploadedFile('respaldo.pdf',b'%PDF-1.4\n%%EOF',content_type='application/pdf')}).json()['data'];url=f"/api/operacion/evidencias/{e['id']}/anular/"
  self.assertEqual(self.post(url,{'_version':e['version'],'motivo':''}).status_code,400)
  self.assertEqual(self.post(url,{'_version':999,'motivo':'No corresponde'}).status_code,409)
  self.assertEqual(self.post(url,{'_version':e['version'],'motivo':'No corresponde'}).status_code,200)
  self.assertTrue(RevisionEvidencia.objects.filter(evidencia_id=e['id'],decision='Anulada',observacion='No corresponde').exists())
  self.assertEqual(self.post(url,{'_version':e['version'],'motivo':'Repetición'}).status_code,409)
 def test_reapertura_preserva_cierre_tardio(self):
  c=self.commitment();url=f"/api/operacion/compromisos/{c['id']}/"
  c=self.client.patch(url,{'_version':c['version'],'estado':'Realizado','observacion':'Cierre tardío'},content_type='application/json').json()['data']
  self.assertEqual(self.post(f"/api/operacion/compromisos/{c['id']}/reabrir/",{'_version':c['version'],'motivo':'Requiere seguimiento adicional'}).status_code,200)
  from .models import CierreCompromiso
  old=CierreCompromiso.objects.get(compromiso_id=c['id']);self.assertEqual(old.dias_atraso,2);self.assertEqual(old.observacion,'Cierre tardío')
 def test_politica_propuesta_versionada_y_conflicto(self):
  p=self.client.get('/api/gobierno/').json()['data']['politica'];data={'_version':p['version'],'motivo':'Revisión local','transiciones':p['transiciones'],'validar':False}
  r=self.post('/api/gobierno/',data);self.assertEqual(r.status_code,200,r.content);self.assertFalse(r.json()['data']['politica']['validada']);self.assertEqual(self.post('/api/gobierno/',data).status_code,409)
 def test_politica_no_valida_roles_obsoletos(self):
  p=self.client.get('/api/gobierno/').json()['data']['politica'];r=self.post('/api/gobierno/',{'_version':p['version'],'motivo':'Prueba','transiciones':p['transiciones'],'validar':True,'roles_versiones':{'inexistente':1}});self.assertEqual(r.status_code,409,r.content)
 def test_cierre_resuelve_alerta_sin_eliminar_revision(self):
  c=self.commitment();a=next(x for x in self.client.get('/api/alertas/').json()['results'] if x['registro']==c['id']);self.post(f"/api/alertas/{a['id']}/revisar/",{'_version':a['version']})
  self.client.patch(f"/api/operacion/compromisos/{c['id']}/",{'_version':c['version'],'estado':'Realizado','observacion':'Entrega realizada'},content_type='application/json')
  a=next(x for x in self.client.get('/api/alertas/').json()['results'] if x['id']==a['id']);self.assertFalse(a['activa']);self.assertTrue(a['revisada']);self.assertIsNotNone(a['resuelta_en'])
