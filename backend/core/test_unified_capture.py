from django.test import TestCase
from django.utils import timezone
from .models import Delegacion,Usuario,Rol,TipoAtencion,SubAtencion,ItemMeta,Actividad,Compromiso,Atencion

class UnifiedCaptureTests(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='UNI',nombre='Delegación QA seguimiento')
  self.other_d=Delegacion.objects.create(codigo='OTR',nombre='Otra QA')
  self.u=Usuario.objects.create_superuser('captura_qa',password='LocalQA!937',delegacion=self.d)
  self.other=Usuario.objects.create_user('responsable_fuera',delegacion=self.other_d)
  self.t=TipoAtencion.objects.create(codigo='T',nombre='Consulta');self.s=SubAtencion.objects.create(codigo='S',nombre='Consulta específica',tipo_atencion=self.t)
  self.i=ItemMeta.objects.create(codigo='I',nombre='Ítem QA')
  self.client.force_login(self.u)
 def follow(self,**extra):return dict(responsable=self.u.pk,fecha_comprometida=str(timezone.localdate()),descripcion='Coordinar respuesta',sector='Sector QA',area_apoyo='Equipo QA',origen='Externo',**extra)
 def attention(self,**extra):return {**dict(solicitante='Persona ficticia',descripcion='Solicitud ciudadana QA',tipo_atencion=self.t.pk,sub_atencion=self.s.pk),**extra}
 def activity(self,**extra):return {**dict(fecha=str(timezone.localdate()),solicitud='Solicitud actividad QA',accion='Visita inicial',contacto='Persona ficticia',telefono='912345678',sector='Sector QA',item=self.i.pk),**extra}
 def post(self,resource,data):return self.client.post('/api/'+resource+'/',data,content_type='application/json')
 def test_atencion_genera_compromiso_vinculado_sin_actividad_intermedia(self):
  r=self.post('atenciones',self.attention(nuevo_compromiso=self.follow(),clave_idempotencia='UNI-AT'));self.assertEqual(r.status_code,201,r.content)
  a=Atencion.objects.get(pk=r.json()['data']['id']);c=Compromiso.objects.get(pk=a.compromiso_id)
  self.assertEqual(c.solicitante,a.solicitante);self.assertEqual(c.delegacion_id,a.delegacion_id);self.assertEqual(c.codigo_verificacion_foto,a.folio);self.assertEqual(Actividad.objects.count(),0)
 def test_actividad_genera_compromiso_y_reintento_no_duplica(self):
  payload=self.activity(nuevo_compromiso=self.follow(),clave_idempotencia='UNI-ACT')
  first=self.post('operacion/actividades',payload);self.assertEqual(first.status_code,201,first.content)
  second=self.post('operacion/actividades',payload);self.assertEqual(second.status_code,200,second.content);self.assertEqual(first.json()['data']['id'],second.json()['data']['id'])
  self.assertEqual(Compromiso.objects.count(),1);a=Actividad.objects.first();self.assertEqual(a.compromiso.codigo_verificacion_foto,a.codigo)
  payload['nuevo_compromiso']['descripcion']='Otro compromiso';self.assertEqual(self.post('operacion/actividades',payload).status_code,409)
 def test_atencion_reintento_conserva_vinculo_y_rechaza_otros_datos(self):
  payload=self.attention(compromiso=None,nuevo_compromiso=self.follow(),clave_idempotencia='UNI-REP')
  first=self.post('atenciones',payload);self.assertEqual(first.status_code,201,first.content)
  self.assertEqual(self.post('atenciones',payload).status_code,200);self.assertEqual(Compromiso.objects.count(),1)
  payload['nuevo_compromiso']['sector']='Otro sector';self.assertEqual(self.post('atenciones',payload).status_code,409)
 def test_sin_seguimiento_no_crea_compromiso(self):
  self.assertEqual(self.post('atenciones',self.attention()).status_code,201)
  self.assertEqual(self.post('operacion/actividades',self.activity()).status_code,201)
  self.assertEqual(Compromiso.objects.count(),0)
 def test_error_de_origen_revierte_compromiso(self):
  r=self.post('operacion/actividades',self.activity(telefono='x',nuevo_compromiso=self.follow()));self.assertEqual(r.status_code,400)
  from unittest.mock import patch
  from django.core.exceptions import ValidationError
  with patch.object(Atencion,'full_clean',side_effect=ValidationError('Fallo de validación del origen')):
   r=self.post('atenciones',self.attention(nuevo_compromiso=self.follow()));self.assertEqual(r.status_code,400)
  self.assertEqual(Compromiso.objects.count(),0);self.assertEqual(Atencion.objects.count(),0);self.assertEqual(Actividad.objects.count(),0)
 def test_error_compromiso_revierte_origen(self):
  bad=self.follow();bad['fecha_comprometida']='2000-01-01'
  for resource,payload in [('atenciones',self.attention(nuevo_compromiso=bad)),('operacion/actividades',self.activity(nuevo_compromiso=bad))]:self.assertEqual(self.post(resource,payload).status_code,400)
  self.assertEqual(Compromiso.objects.count(),0);self.assertEqual(Atencion.objects.count(),0);self.assertEqual(Actividad.objects.count(),0)
 def test_responsable_ajeno_rechazado(self):
  data=self.follow();data['responsable']=self.other.pk
  self.assertEqual(self.post('atenciones',self.attention(nuevo_compromiso=data)).status_code,400);self.assertEqual(Compromiso.objects.count(),0)
 def test_sin_permiso_de_compromiso_no_crea_ningun_registro(self):
  role=Rol.objects.create(nombre='Captura sin tubo',permisos=['atenciones.crear','actividades.crear'])
  self.u.is_superuser=False;self.u.rol=role;self.u.save()
  self.assertEqual(self.post('atenciones',self.attention(nuevo_compromiso=self.follow())).status_code,403)
  self.assertEqual(self.post('operacion/actividades',self.activity(nuevo_compromiso=self.follow())).status_code,403)
  self.assertEqual(Compromiso.objects.count(),0)
 def test_nuevo_y_existente_excluyentes_y_campos_delegacion_rechazados(self):
  c=Compromiso.objects.create(autor=self.u,delegacion=self.d,descripcion='Anterior',solicitante='QA',sector='QA',responsable=self.u,fecha_comprometida=timezone.localdate(),area_apoyo='QA',origen='Interno')
  r=self.post('atenciones',self.attention(compromiso=c.pk,nuevo_compromiso=self.follow()));self.assertEqual(r.status_code,400)
  data=self.follow();data['delegacion']=self.other_d.pk
  self.assertEqual(self.post('operacion/actividades',self.activity(nuevo_compromiso=data)).status_code,400);self.assertEqual(Compromiso.objects.count(),1)
 def test_origenes_del_tubo_respetan_permisos(self):
  r=self.post('atenciones',self.attention(nuevo_compromiso=self.follow()));self.assertEqual(r.status_code,201,r.content)
  c=r.json()['data']['compromiso'];response=self.client.get(f'/api/operacion/compromisos/{c}/origenes/');self.assertEqual(response.status_code,200,response.content);self.assertEqual(response.json()['results'][0]['tipo'],'atencion')
  role=Rol.objects.create(nombre='Tubo sin atenciones',permisos=['compromisos.ver','compromisos.ver_equipo']);self.u.is_superuser=False;self.u.rol=role;self.u.save()
  response=self.client.get(f'/api/operacion/compromisos/{c}/origenes/');self.assertEqual(response.status_code,200);self.assertEqual(response.json()['results'],[])


 def test_cuarta_gestion_social_no_deja_compromiso_huerfano(self):
  first=self.post('atenciones',self.attention(nuevo_caso=True,nuevo_compromiso=self.follow()));self.assertEqual(first.status_code,201,first.content)
  code=first.json()['data']['caso_social']
  for stage in [2,3]:self.assertEqual(self.post('atenciones',self.attention(caso_social=code)).status_code,201)
  self.assertEqual(self.post('atenciones',self.attention(caso_social=code,nuevo_compromiso=self.follow())).status_code,409)
  self.assertEqual(Compromiso.objects.count(),1);self.assertEqual(Atencion.objects.count(),3)
 def test_opciones_y_origenes_no_exponen_otra_delegacion(self):
  response=self.client.get('/api/seguimiento/opciones/');self.assertEqual(response.status_code,200)
  self.assertNotIn(self.other.pk,{u['id'] for u in response.json()['responsables']})
  r=self.post('atenciones',self.attention(nuevo_compromiso=self.follow()));c=r.json()['data']['compromiso']
  session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save()
  self.assertEqual(self.client.get(f'/api/operacion/compromisos/{c}/origenes/').status_code,404)

from django.test import TransactionTestCase,Client
from django.db import close_old_connections
from concurrent.futures import ThreadPoolExecutor

class ConcurrentUnifiedCaptureTests(TransactionTestCase):
 setUp=UnifiedCaptureTests.setUp
 follow=UnifiedCaptureTests.follow
 attention=UnifiedCaptureTests.attention
 activity=UnifiedCaptureTests.activity
 def test_reintentos_simultaneos_no_duplican_origen_ni_compromiso(self):
  for resource,payload in [('atenciones',self.attention(compromiso=None,nuevo_compromiso=self.follow(),clave_idempotencia='UNI-CONCURRENT-AT')),('operacion/actividades',self.activity(compromiso=None,nuevo_compromiso=self.follow(),clave_idempotencia='UNI-CONCURRENT-ACT'))]:
   def capture(index):
    close_old_connections()
    try:
     client=Client();client.force_login(Usuario.objects.get(pk=self.u.pk))
     response=client.post('/api/'+resource+'/',payload,content_type='application/json')
     return response.status_code,response.json()
    finally:close_old_connections()
   with ThreadPoolExecutor(max_workers=3) as executor:results=list(executor.map(capture,range(3)))
   for status,data in results:self.assertIn(status,[200,201],data)
   self.assertEqual(len({data['data']['id'] for _,data in results}),1)
  self.assertEqual(Atencion.objects.count(),1);self.assertEqual(Actividad.objects.count(),1);self.assertEqual(Compromiso.objects.count(),2)
