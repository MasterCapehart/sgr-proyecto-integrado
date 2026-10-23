from django.test import TestCase
from django.utils import timezone
from . import test_capture_form as helpers
from .models import Usuario,Rol,Actividad,Compromiso,Atencion

class FollowupAssignmentTests(TestCase):
 payload=helpers.CaptureFormTests.payload
 activity=helpers.CaptureFormTests.activity
 follow=helpers.CaptureFormTests.follow
 def setUp(self):
  helpers.CaptureFormTests.setUp(self)
  self.peer=Usuario.objects.create_user('otro_funcionario_asignacion',delegacion=self.d)
  self.role=Rol.objects.create(nombre='Funcionario',permisos=['actividades.ver','actividades.crear','actividades.editar','compromisos.ver','compromisos.crear','compromisos.editar','atenciones.ver','atenciones.crear'])
  self.u.is_superuser=False;self.u.rol=self.role;self.u.save()
 def send(self,url,data,method='post'):return getattr(self.client,method)(url,data,content_type='application/json')
 def commitment(self,**extra):return dict(descripcion='Seguimiento ficticio',solicitante='Vecino ficticio',sector='Territorio ficticio',fecha_comprometida=str(timezone.localdate()),origen='Externo',**extra)
 def test_alta_directa_automatica_propia_sin_apoyo_ni_unidad(self):
  r=self.send('/api/operacion/compromisos/',self.commitment());self.assertEqual(r.status_code,201,r.content);row=r.json()['data'];self.assertEqual(row['responsable'],self.u.pk);self.assertEqual(row['area_apoyo'],'');self.assertEqual(row['unidad'],1)
 def test_funcionario_no_asigna_otro_en_altas_atomicas(self):
  follow=self.follow();follow['responsable']=self.peer.pk
  captures=[('/api/captura/',self.payload(nuevo_compromiso=follow)),('/api/operacion/actividades/',self.activity(nuevo_compromiso=follow)),('/api/atenciones/',dict(solicitante='Vecino ficticio',tipo_atencion=self.t.pk,sub_atencion=self.s.pk,descripcion='Atención ficticia',nuevo_compromiso=follow)),('/api/operacion/compromisos/',self.commitment(responsable=self.peer.pk))]
  for url,payload in captures:
   with self.subTest(ruta=url):self.assertEqual(self.send(url,payload).status_code,403)
  self.assertEqual(Compromiso.objects.count(),0);self.assertEqual(Actividad.objects.count(),0);self.assertEqual(Atencion.objects.count(),0)
 def test_no_reasigna_al_editar_y_no_cambia_version(self):
  r=self.send('/api/operacion/compromisos/',self.commitment(responsable=self.u.pk));self.assertEqual(r.status_code,201,r.content);row=r.json()['data'];r=self.send(f"/api/operacion/compromisos/{row['id']}/",dict(_version=row['version'],responsable=self.peer.pk,observacion='No puede reasignar'),'patch');self.assertEqual(r.status_code,403,r.content);obj=Compromiso.objects.get();self.assertEqual(obj.version,row['version']);self.assertEqual(obj.responsable_id,self.u.pk)
 def test_permiso_explicito_de_equipo_autoriza_asignacion(self):
  self.role.nombre='Coordinador';self.role.permisos+=['compromisos.editar_equipo'];self.role.save();r=self.send('/api/operacion/compromisos/',self.commitment(responsable=self.peer.pk));self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['responsable'],self.peer.pk)
 def test_administrador_superusuario_conserva_asignacion(self):
  self.u.is_superuser=True;self.u.save();r=self.send('/api/captura/',self.payload(nuevo_compromiso={**self.follow(),'responsable':self.peer.pk}));self.assertEqual(r.status_code,201,r.content);self.assertEqual(Compromiso.objects.get().responsable_id,self.peer.pk)
 def test_opciones_no_confunden_asignables_y_profesionales(self):
  r=self.client.get('/api/captura/opciones/');self.assertEqual(r.status_code,200,r.content);o=r.json();self.assertFalse(o['puede_asignar_responsable']);self.assertEqual([u['id'] for u in o['responsables_compromiso']],[self.u.pk]);self.assertIn(self.peer.pk,[u['id'] for u in o['responsables']])
  o=self.client.get('/api/seguimiento/opciones/').json();self.assertEqual([u['id'] for u in o['responsables']],[self.u.pk])
 def test_funcionario_sigue_compromiso_asignado_sin_reasignarlo(self):
  obj=Compromiso.objects.create(autor=self.peer,delegacion=self.d,responsable=self.u,fecha_comprometida=timezone.localdate(),descripcion='Asignado',solicitante='Vecino',sector='Territorio',origen='Interno')
  r=self.send(f'/api/operacion/compromisos/{obj.pk}/',dict(_version=obj.version,responsable=self.u.pk,estado='En proceso',observacion='Avance propio'),'patch');self.assertEqual(r.status_code,200,r.content)
