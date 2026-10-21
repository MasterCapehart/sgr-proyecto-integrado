import uuid
from django.test import TestCase
from . import test_unified_capture as helpers
from .models import Actividad,Atencion,Compromiso,Rol

class CaptureFormTests(TestCase):
 setUp=helpers.UnifiedCaptureTests.setUp
 activity=helpers.UnifiedCaptureTests.activity
 follow=helpers.UnifiedCaptureTests.follow
 def payload(self,**extra):return dict(clave_idempotencia=uuid.uuid4().hex,actividad=self.activity(junta_vecinos='JJVV de prueba'),**extra)
 def post(self,data):return self.client.post('/api/captura/',data,content_type='application/json')
 def social(self,**extra):return {**dict(tipo_atencion=self.t.pk,sub_atencion=self.s.pk,nuevo_caso=True),**extra}
 def test_registro_comun_guarda_junta_una_vez(self):
  data=self.payload();r=self.post(data);self.assertEqual(r.status_code,201,r.content)
  self.assertEqual(Actividad.objects.get().junta_vecinos,'JJVV de prueba');self.assertEqual(Atencion.objects.count(),0)
  self.assertEqual(self.post(data).status_code,200);self.assertEqual(Actividad.objects.count(),1)
  data['actividad']['junta_vecinos']='Otro';self.assertEqual(self.post(data).status_code,409)
 def test_social_y_tubo_se_vinculan_a_un_solo_registro(self):
  data=self.payload(social=self.social(),nuevo_compromiso=self.follow());r=self.post(data);self.assertEqual(r.status_code,201,r.content)
  a=Actividad.objects.get();self.assertEqual(a.atencion_id,Atencion.objects.get().pk);self.assertEqual(a.compromiso_id,Atencion.objects.get().compromiso_id)
  self.assertEqual(Compromiso.objects.count(),1);self.assertEqual(self.post(data).status_code,200)
  data['social']['nuevo_caso']=False;self.assertEqual(self.post(data).status_code,409)
 def test_error_social_no_deja_actividad_o_tubo(self):
  r=self.post(self.payload(social=self.social(sub_atencion=99999),nuevo_compromiso=self.follow()));self.assertEqual(r.status_code,400,r.content)
  self.assertFalse(Actividad.objects.exists());self.assertFalse(Compromiso.objects.exists());self.assertFalse(Atencion.objects.exists())
 def test_sin_permiso_social_no_escribe(self):
  self.u.is_superuser=False;self.u.rol=Rol.objects.create(nombre='Solo actividades',permisos=['actividades.crear']);self.u.save()
  r=self.post(self.payload(social=self.social()));self.assertEqual(r.status_code,403,r.content);self.assertFalse(Actividad.objects.exists())
 def test_cuarta_gestion_revierte_todo(self):
  first=self.post(self.payload(social=self.social()));self.assertEqual(first.status_code,201,first.content)
  case=Atencion.objects.get().caso_social
  for _ in range(2):self.assertEqual(self.post(self.payload(social=self.social(nuevo_caso=False,caso_social=case))).status_code,201)
  self.assertEqual(self.post(self.payload(social=self.social(nuevo_caso=False,caso_social=case),nuevo_compromiso=self.follow())).status_code,409)
  self.assertEqual(Actividad.objects.count(),3);self.assertEqual(Atencion.objects.count(),3);self.assertEqual(Compromiso.objects.count(),0)
 def test_rechaza_autor_o_delegacion_inyectados(self):
  data=self.payload();data['actividad']['delegacion']=self.other_d.pk
  self.assertEqual(self.post(data).status_code,400);self.assertFalse(Actividad.objects.exists())
 def test_sin_permiso_tubo_revierte_social(self):
  self.u.is_superuser=False;self.u.rol=Rol.objects.create(nombre='Sin tubo captura',permisos=['actividades.crear','atenciones.crear']);self.u.save()
  r=self.post(self.payload(social=self.social(),nuevo_compromiso=self.follow()));self.assertEqual(r.status_code,403,r.content)
  self.assertEqual(Atencion.objects.count(),0);self.assertEqual(Actividad.objects.count(),0)

 def test_opciones_para_capturar_sin_administrar_catalogos(self):
  self.u.is_superuser=False;self.u.rol=Rol.objects.create(nombre='Captura sin catálogo',permisos=['actividades.crear','atenciones.crear']);self.u.save()
  r=self.client.get('/api/captura/opciones/');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(r.json()['tipos'][0]['id'],self.t.pk)
