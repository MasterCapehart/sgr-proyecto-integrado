import uuid
from django.test import TestCase
from . import test_capture_form as helpers
from .models import Rol,Usuario,Actividad

class EligibilityTests(TestCase):
 setUp=helpers.CaptureFormTests.setUp
 payload=helpers.CaptureFormTests.payload
 activity=helpers.CaptureFormTests.activity
 def send(self,url,data,method='post'):return getattr(self.client,method)(url,data,content_type='application/json')
 def rule(self,kind='Ejecución',enabled=True,version=0):
  r=self.send(f'/api/clasificacion-actividades/{self.i.pk}/',dict(_version=version,clasificacion=kind,valida_para_puntuar=enabled,motivo='Definición de catálogo QA',clave_idempotencia=uuid.uuid4().hex));self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def capture(self,**values):
  p=self.payload();p['actividad'].update(values);r=self.send('/api/captura/',p);self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_ejecucion_valida_candidata_sin_otorgar_puntos(self):
  self.rule();a=self.capture();self.assertTrue(a['elegibilidad']['potencialmente_puntuable']);self.assertEqual(a['elegibilidad']['clasificacion'],'Ejecución');self.assertNotIn('puntaje',a['elegibilidad'])
 def test_coordinacion_y_otra_gestion_no_puntuan(self):
  for kind in ['Coordinación','Otra gestión']:
   self.rule(kind,False,0 if kind=='Coordinación' else 1);a=self.capture();self.assertFalse(a['elegibilidad']['potencialmente_puntuable']);self.assertTrue(a['elegibilidad']['motivos'])
 def test_datos_faltantes_se_conservan_y_no_candidatos(self):
  self.rule();a=self.capture(contacto='',telefono='');self.assertFalse(a['elegibilidad']['potencialmente_puntuable']);self.assertEqual(a['contacto'],'');self.assertEqual(a['telefono'],'');self.assertGreaterEqual(len(a['elegibilidad']['motivos']),2)
 def test_delegado_beneficiario_no_confundir_autor(self):
  self.rule();role=Rol.objects.create(nombre='Delegado',permisos=[]);delegate=Usuario.objects.create_user('delegado_beneficiario',rol=role,delegacion=self.d,rut='12345678-5')
  self.u.rol=role;self.u.save();a=self.capture();self.assertTrue(a['elegibilidad']['potencialmente_puntuable'])
  a=self.capture(beneficiario_usuario=delegate.pk);self.assertEqual(a['elegibilidad']['clasificacion'],'Otra gestión');self.assertFalse(a['elegibilidad']['potencialmente_puntuable'])
  a=self.capture(rut_contacto='12345678-5');self.assertFalse(a['elegibilidad']['potencialmente_puntuable'])
 def test_catalogo_cambia_no_reescribe_historia(self):
  self.rule();a=self.capture();self.rule('Coordinación',False,1)
  old=self.client.get(f'/api/operacion/actividades/{a["id"]}/').json()['data'];self.assertTrue(old['elegibilidad']['potencialmente_puntuable']);self.assertEqual(old['elegibilidad']['regla']['version'],1)
  r=self.send(f'/api/operacion/actividades/{a["id"]}/',dict(_version=a['version'],accion='Texto actualizado'),'patch');self.assertEqual(r.status_code,200,r.content);self.assertTrue(r.json()['data']['elegibilidad']['potencialmente_puntuable']);self.assertFalse(self.capture()['elegibilidad']['potencialmente_puntuable'])
 def test_sin_regla_y_sin_evaluacion_historica_no_puntuan(self):
  a=self.capture();self.assertFalse(a['elegibilidad']['potencialmente_puntuable']);Actividad.objects.filter(pk=a['id']).update(elegibilidad_snapshot=None)
  self.rule();old=self.client.get(f'/api/operacion/actividades/{a["id"]}/').json()['data'];self.assertFalse(old['elegibilidad']['potencialmente_puntuable']);self.assertEqual(old['elegibilidad']['estado'],'Sin evaluación histórica')
 def test_permisos_contexto_y_prohibicion_de_snapshot_inyectado(self):
  self.rule();self.u.is_superuser=False;self.u.rol=Rol.objects.create(nombre='Funcionario elegibilidad QA',permisos=['actividades.crear']);self.u.save()
  self.assertEqual(self.send(f'/api/clasificacion-actividades/{self.i.pk}/',{}).status_code,403)
  p=self.payload();p['actividad']['elegibilidad_snapshot']={};self.assertEqual(self.send('/api/captura/',p).status_code,400)
  p=self.payload();p['actividad']['beneficiario_usuario']=self.other.pk;self.assertEqual(self.send('/api/captura/',p).status_code,400)
 def test_version_y_coordinacion_habilitada_invalida(self):
  self.rule();r=self.send(f'/api/clasificacion-actividades/{self.i.pk}/',dict(_version=0,clasificacion='Coordinación',valida_para_puntuar=False,motivo='QA',clave_idempotencia=uuid.uuid4().hex));self.assertEqual(r.status_code,409)
  r=self.send(f'/api/clasificacion-actividades/{self.i.pk}/',dict(_version=1,clasificacion='Coordinación',valida_para_puntuar=True,motivo='QA',clave_idempotencia=uuid.uuid4().hex));self.assertEqual(r.status_code,400)
 def test_social_sin_datos_conserva_evaluacion(self):
  self.rule();p=self.payload(social=helpers.CaptureFormTests.social(self));p['actividad'].update(contacto='',telefono='');r=self.send('/api/captura/',p);self.assertEqual(r.status_code,201,r.content);self.assertFalse(r.json()['data']['elegibilidad']['potencialmente_puntuable'])
 def test_run_formateado_del_delegado_no_evade_clasificacion(self):
  self.rule();role=Rol.objects.create(nombre='Delegado',permisos=[]);Usuario.objects.create_user('delegado_run_formateado',rol=role,delegacion=self.d,rut='12.345.678-5')
  a=self.capture(rut_contacto='12345678-5');self.assertFalse(a['elegibilidad']['potencialmente_puntuable']);self.assertEqual(a['elegibilidad']['clasificacion'],'Otra gestión')
 def test_reglas_se_aislan_por_delegacion_y_reintento_no_duplica(self):
  r=self.rule();payload=dict(_version=1,clasificacion='Coordinación',valida_para_puntuar=False,motivo='Nueva definición',clave_idempotencia=uuid.uuid4().hex)
  first=self.send(f'/api/clasificacion-actividades/{self.i.pk}/',payload);repeat=self.send(f'/api/clasificacion-actividades/{self.i.pk}/',payload);self.assertEqual(first.status_code,201,first.content);self.assertEqual(repeat.status_code,200,repeat.content);self.assertEqual(first.json()['data']['id'],repeat.json()['data']['id'])
  s=self.client.session;s['delegacion_activa']=self.other_d.pk;s.save();detail=self.client.get(f'/api/clasificacion-actividades/{self.i.pk}/').json()['data'];self.assertIsNone(detail['regla']);self.assertEqual(detail['historial'],[])
 def test_nombre_ausente_no_bloquea_seguimiento(self):
  self.rule();p=self.payload(nuevo_compromiso=helpers.CaptureFormTests.follow(self));p['actividad'].update(contacto='',telefono='');r=self.send('/api/captura/',p);self.assertEqual(r.status_code,201,r.content);self.assertIsNotNone(r.json()['data']['compromiso']);self.assertFalse(r.json()['data']['elegibilidad']['potencialmente_puntuable'])
