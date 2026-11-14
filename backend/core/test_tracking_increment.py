from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from . import test_unified_capture as helpers
from .models import Rol,Usuario,Compromiso,Actividad,RegistroGestion

class TrackingIncrementTests(TestCase):
 setUp=helpers.UnifiedCaptureTests.setUp
 def send(self,url,data,method='post'):return getattr(self.client,method)(url,data,content_type='application/json')
 def commitment(self,**extra):
  payload=dict(descripcion='Seguimiento ficticio',solicitante='Persona ficticia',sector='Sector QA',fecha_comprometida=str(timezone.localdate()+timedelta(days=2)),origen='Externo');payload.update(extra)
  r=self.send('/api/operacion/compromisos/',payload);self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_realizado_no_es_cerrado_y_resultado_obligatorio(self):
  c=self.commitment();self.assertEqual(c['estado'],'Pendiente')
  r=self.send(f'/api/operacion/compromisos/{c["id"]}/',{'_version':c['version'],'estado':'Realizado','observacion':'Acción ejecutada'},'patch');self.assertEqual(r.status_code,200,r.content);c=r.json()['data'];self.assertIsNone(c['fecha_cierre'])
  self.assertEqual(self.send(f'/api/operacion/compromisos/{c["id"]}/',{'_version':c['version'],'estado':'Cerrado','observacion':'Cerrar'},'patch').status_code,400)
  r=self.send(f'/api/operacion/compromisos/{c["id"]}/',{'_version':c['version'],'estado':'Cerrado','resultado':'Solicitud resuelta','observacion':'Cierre documentado'},'patch');self.assertEqual(r.status_code,200,r.content);c=r.json()['data'];self.assertTrue(c['fecha_cierre']);self.assertEqual(c['resultado'],'Solicitud resuelta')
 def test_companero_consulta_pero_autor_reasignado_no_edita(self):
  c=self.commitment();r=Rol.objects.create(nombre='Funcionario tracking',permisos=['compromisos.ver','compromisos.editar','compromisos.crear'])
  owner=Usuario.objects.create_user('otro_tracking',delegacion=self.d,rol=r)
  result=self.send(f'/api/operacion/compromisos/{c["id"]}/',{'_version':c['version'],'responsable':owner.pk,'observacion':'Reasignación justificada'},'patch');self.assertEqual(result.status_code,200,result.content);c=result.json()['data']
  self.u.is_superuser=False;self.u.rol=r;self.u.save()
  self.assertEqual(self.client.get(f'/api/operacion/compromisos/{c["id"]}/').status_code,200)
  self.assertEqual(self.send(f'/api/operacion/compromisos/{c["id"]}/',{'_version':c['version'],'estado':'En proceso','observacion':'Autor antiguo'},'patch').status_code,403)
 def test_fuente_unica_compartida_y_cambio_comun_bloqueado_en_tubo(self):
  a=self.send('/api/operacion/actividades/',helpers.UnifiedCaptureTests.activity(self,nuevo_compromiso=helpers.UnifiedCaptureTests.follow(self))).json()['data'];c=Compromiso.objects.get(pk=a['compromiso']);activity=Actividad.objects.get(pk=a['id'])
  self.assertTrue(activity.registro_gestion_id);self.assertEqual(activity.registro_gestion_id,c.registro_gestion_id)
  r=self.send(f'/api/operacion/compromisos/{c.pk}/',{'_version':c.version,'descripcion':'Contradicción','observacion':'Prueba'},'patch');self.assertEqual(r.status_code,400,r.content)
 def test_compromiso_directo_no_finge_ejecucion_y_no_aplica_exige_motivo(self):
  c=self.commitment();self.assertEqual(Actividad.objects.count(),0);self.assertTrue(c['registro_gestion'])
  r=self.send(f'/api/operacion/compromisos/{c["id"]}/',{'_version':c['version'],'estado':'No aplica','resultado':'Fuera de competencia','observacion':'Derivado por competencia'},'patch');self.assertEqual(r.status_code,200,r.content);self.assertFalse(r.json()['data']['vencido'])
 def test_vinculo_ajeno_no_permite_secuestrar_cabecera(self):
  c=self.commitment();r=Rol.objects.create(nombre='Capturador sin seguimiento',permisos=['actividades.crear','compromisos.ver'])
  other=Usuario.objects.create_user('capturador_ajeno',delegacion=self.d,rol=r,cargo=self.u.cargo);self.client.force_login(other)
  result=self.send('/api/operacion/actividades/',helpers.UnifiedCaptureTests.activity(self,compromiso=c['id']))
  self.assertEqual(result.status_code,403,result.content)
  self.assertEqual(Compromiso.objects.get(pk=c['id']).registro_gestion_id,c['registro_gestion'])
 def test_vinculo_reutiliza_cabecera_y_rechaza_segundo_origen(self):
  c=self.commitment();date=str(timezone.localdate()-timedelta(days=1));data=helpers.UnifiedCaptureTests.activity(self,compromiso=c['id'],fecha=date)
  r=self.send('/api/operacion/actividades/',data);self.assertEqual(r.status_code,201,r.content)
  a=Actividad.objects.get(pk=r.json()['data']['id']);self.assertEqual(a.registro_gestion_id,c['registro_gestion']);self.assertEqual(str(Compromiso.objects.get(pk=c['id']).fecha_solicitud),date)
  second=self.send('/api/operacion/actividades/',helpers.UnifiedCaptureTests.activity(self,compromiso=c['id']))
  self.assertEqual(second.status_code,400,second.content)
 def test_vinculo_cerrado_no_modifica_seguimiento(self):
  c=self.commitment();Compromiso.objects.filter(pk=c['id']).update(estado='Cerrado')
  r=self.send('/api/operacion/actividades/',helpers.UnifiedCaptureTests.activity(self,compromiso=c['id']))
  self.assertEqual(r.status_code,400,r.content)
 def test_fecha_solicitud_y_ficha_social_siguen_fuente(self):
  import uuid
  payload=dict(clave_idempotencia=uuid.uuid4().hex,actividad=helpers.UnifiedCaptureTests.activity(self),social=dict(tipo_atencion=self.t.pk,sub_atencion=self.s.pk,nuevo_caso=True),nuevo_compromiso=helpers.UnifiedCaptureTests.follow(self))
  r=self.send('/api/captura/',payload);self.assertEqual(r.status_code,201,r.content)
  a=Actividad.objects.get(pk=r.json()['data']['id']);date=str(a.fecha)
  changed=self.send(f'/api/operacion/actividades/{a.pk}/',dict(_version=a.version,fecha=date,solicitud='Materia corregida',contacto='Contacto corregido',telefono='912345678',accion='Acción corregida'),'patch');self.assertEqual(changed.status_code,200,changed.content)
  c=self.client.get(f'/api/operacion/compromisos/{a.compromiso_id}/').json()['data'];self.assertEqual(c['fecha_solicitud'],date)
  social=self.client.get(f'/api/atenciones/{a.atencion_id}/').json()['data'];self.assertEqual(social['descripcion'],'Materia corregida');self.assertEqual(social['solicitante'],'Contacto corregido');self.assertEqual(social['gestion_realizada'],'Acción corregida')
 def test_atencion_no_secuestra_compromiso_ajeno(self):
  import uuid
  c=self.commitment();role=Rol.objects.create(nombre='Capturador social sin edición',permisos=['atenciones.crear','compromisos.ver'])
  other=Usuario.objects.create_user('capturador_social_ajeno',delegacion=self.d,rol=role);self.client.force_login(other)
  data=helpers.UnifiedCaptureTests.attention(self,compromiso=c['id'],clave_idempotencia=uuid.uuid4().hex)
  r=self.send('/api/atenciones/',data);self.assertEqual(r.status_code,403,r.content)
  self.assertEqual(Compromiso.objects.get(pk=c['id']).registro_gestion_id,c['registro_gestion'])
 def test_migracion_detecta_origenes_ambiguos_antes_de_modificar(self):
  import importlib
  from types import SimpleNamespace
  from django.apps import apps
  from django.db import connection
  c=self.commitment();a=self.send('/api/operacion/actividades/',helpers.UnifiedCaptureTests.activity(self)).json()['data']
  first=Actividad.objects.get(pk=a['id']);first.compromiso_id=c['id'];first.save()
  first.pk=None;first.codigo='QA-MIGRACION-SEGUNDO';first.registro_gestion_id=None;first.save()
  count=RegistroGestion.objects.count()
  with self.assertRaisesRegex(RuntimeError,'varios orígenes'):
   importlib.import_module('core.migrations.0035_conectar_registros_existentes').connect(apps,SimpleNamespace(connection=connection))
  self.assertEqual(RegistroGestion.objects.count(),count)
 def test_funcionario_con_permiso_equipo_no_reasigna(self):
  role=Rol.objects.create(nombre='Funcionario',permisos=['compromisos.crear','compromisos.ver','compromisos.editar_equipo']);self.u.is_superuser=False;self.u.rol=role;self.u.save()
  target=Usuario.objects.create_user('destino_no_autorizado',delegacion=self.d)
  r=self.send('/api/operacion/compromisos/',dict(descripcion='Prueba negativa',sector='QA',responsable=target.pk,fecha_comprometida=str(timezone.localdate()),origen='Interno'))
  self.assertEqual(r.status_code,403,r.content)

 def test_fecha_social_respeta_dia_local_santiago(self):
  from datetime import datetime,timezone as dt_timezone
  from .models import Atencion
  from .tracking import shared_values
  a=Atencion(fecha_registro=datetime(2026,11,14,1,0,tzinfo=dt_timezone.utc),descripcion='QA',solicitante='QA')
  with timezone.override('America/Santiago'):
   self.assertEqual(str(shared_values(a)['fecha_solicitud']),'2026-11-13')
