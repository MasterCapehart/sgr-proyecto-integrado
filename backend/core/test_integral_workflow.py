"""Aceptación transversal de seis perfiles; datos ficticios y almacenamiento temporal."""
import importlib
import tempfile
import uuid
from datetime import datetime,date,timezone as dt_timezone
from decimal import Decimal
from unittest.mock import patch
from django.apps import apps
from django.test import TestCase,override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from . import test_performance as fixtures, local_api
from .models import Rol,Usuario,Actividad,Atencion,Compromiso,TipoAtencion,SubAtencion

class IntegralWorkflowTests(TestCase):
 calendar=fixtures.PerformanceTests.calendar
 send=fixtures.PerformanceTests.send
 summary=fixtures.PerformanceTests.summary
 def setUp(self):
  now=patch('django.utils.timezone.now',return_value=datetime(2026,2,10,15,tzinfo=dt_timezone.utc));now.start();self.addCleanup(now.stop)
  today=patch('django.utils.timezone.localdate',return_value=date(2026,2,10));today.start();self.addCleanup(today.stop)
  tmp=tempfile.TemporaryDirectory(prefix='sgr-integral-');self.addCleanup(tmp.cleanup);settings=override_settings(MEDIA_ROOT=tmp.name);settings.enable();self.addCleanup(settings.disable)
  fixtures.PerformanceTests.setUp(self)
  self.role.permisos=list(local_api.PERMISSIONS);self.role.save()
  basic=['actividades.ver','actividades.crear','actividades.editar','compromisos.ver','compromisos.crear','compromisos.editar','evidencias.ver','evidencias.crear','atenciones.ver','atenciones.crear','conversaciones.crear']
  self.worker.rol.permisos=basic;self.worker.rol.save()
  profiles={'Administrador':list(local_api.PERMISSIONS),'Coordinador':['actividades.ver','actividades.ver_equipo','compromisos.ver','compromisos.ver_equipo','compromisos.editar','compromisos.editar_equipo','evidencias.ver','evidencias.ver_equipo','reportes.ver'], 'Verificador':['actividades.ver','actividades.ver_equipo','evidencias.ver','evidencias.revisar'],'Consulta':['actividades.ver','actividades.ver_equipo','compromisos.ver','compromisos.ver_equipo','evidencias.ver','evidencias.ver_equipo','reportes.ver']}
  self.users={'Delegado':self.u,'Funcionario':self.worker}
  for label,permissions in profiles.items():
   role=Rol.objects.create(nombre=label,permisos=permissions);self.users[label]=Usuario.objects.create_user('integral_'+label.lower(),rol=role,delegacion=self.d)
  for name,function in [('0022_organizaciones_pertenencias','grant_community_permissions'),('0023_hitos_festividades','grant_permissions'),('0024_clasificacion_elegibilidad','grant_permissions'),('0027_ausencias_y_calendario','grant_permissions')]:getattr(importlib.import_module('core.migrations.'+name),function)(apps,None)
  for user in self.users.values():user.rol.refresh_from_db()
  self.kind=TipoAtencion.objects.create(codigo='INT',nombre='Atención integral');self.sub=SubAtencion.objects.create(codigo='INT',nombre='Orientación integral',tipo_atencion=self.kind)
 def post(self,url,data,status=201):
  r=self.send(url,data);self.assertEqual(r.status_code,status,r.content);return r.json()['data']
 def capture(self,neighbor=None,follow=True):
  data=dict(clave_idempotencia=uuid.uuid4().hex,actividad=dict(fecha='2026-02-10',solicitud='Atención integral ficticia',accion='Ejecución final',contacto='Vecino integral ficticio',telefono='912345678',sector='Territorio ficticio',item=self.i.pk,junta_vecinos='Junta integral ficticia'))
  if neighbor:data['vecino']=neighbor
  if follow:
   data['social']=dict(tipo_atencion=self.kind.pk,sub_atencion=self.sub.pk,nuevo_caso=True)
   data['nuevo_compromiso']=dict(responsable=self.worker.pk,fecha_comprometida='2026-02-12',origen='Externo')
  return self.post('/api/captura/',data)
 def define_rule(self):
  self.client.force_login(self.u);return self.post(f'/api/clasificacion-actividades/{self.i.pk}/',dict(_version=0,clasificacion='Ejecución',valida_para_puntuar=True,motivo='Regla de aceptación integral',clave_idempotencia=uuid.uuid4().hex))
 def test_recorrido_vecino_social_tubo_evidencia_metas_colectivo_y_cierre(self):
  self.define_rule()
  organization=self.post('/api/organizaciones/',dict(nombre='Junta integral ficticia',tipo='Junta de vecinos',territorio='Territorio ficticio',clave_idempotencia=uuid.uuid4().hex))
  self.client.force_login(self.worker)
  neighbor=self.post('/api/vecinos/',dict(nombre='Vecino integral ficticio',telefono='912345678',sector='Territorio ficticio',clave_idempotencia=uuid.uuid4().hex))
  self.client.force_login(self.u);membership=self.post('/api/pertenencias/',dict(vecino=neighbor['id'],organizacion=organization['id'],rol='Dirigente'));self.assertEqual(membership['rol'],'Dirigente')
  self.client.force_login(self.worker);a=self.capture(neighbor['id']);self.assertTrue(a['elegibilidad']['potencialmente_puntuable']);self.assertIsNotNone(a['compromiso']);self.assertIsNotNone(a['atencion']);self.assertEqual(Compromiso.objects.count(),1)
  c=Compromiso.objects.get();self.assertEqual(c.codigo_verificacion_foto,a['codigo']);self.assertEqual(Atencion.objects.get().compromiso_id,c.pk)
  r=self.client.post('/api/operacion/evidencias/',dict(actividad=a['id'],descripcion='Respaldo de ejecución ficticia',archivo=SimpleUploadedFile('integral.pdf',b'%PDF-1.4\n%%EOF',content_type='application/pdf')));self.assertEqual(r.status_code,201,r.content);e=r.json()['data']
  self.assertEqual(self.send(f"/api/operacion/evidencias/{e['id']}/revisar/",dict(_version=e['version'],decision='Aprobada',observacion='Autorrevisión no autorizada')).status_code,403)
  self.worker.rol.permisos.append('evidencias.revisar');self.worker.rol.save()
  self.assertEqual(self.send(f"/api/operacion/evidencias/{e['id']}/revisar/",dict(_version=e['version'],decision='Aprobada',observacion='No autorrevisión aunque tenga permiso')).status_code,400)
  self.worker.rol.permisos.remove('evidencias.revisar');self.worker.rol.save()
  self.client.force_login(self.users['Verificador']);self.post(f"/api/operacion/evidencias/{e['id']}/revisar/",dict(_version=e['version'],decision='Aprobada',observacion='Ejecución verificada por otra persona'),200)
  self.client.force_login(self.worker);self.assertEqual(self.summary()['metas'][0]['cumplimiento'],'10.00')
  self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).status_code,403)
  self.client.force_login(self.users['Coordinador'])
  r=self.send(f'/api/operacion/compromisos/{c.pk}/',dict(_version=c.version,estado='En proceso',observacion='Seguimiento integral'),'patch');self.assertEqual(r.status_code,200,r.content)
  self.client.force_login(self.u);before=self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).json()['data'];self.assertEqual(before['items'][0]['reconocido'],'1.00')
  self.post(f'/api/periodos/{self.p.pk}/cerrar/',dict(_version=self.p.version,motivo='Aceptación integral'),200)
  frozen=self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).json()['data'];self.assertTrue(frozen['cerrado']);self.assertEqual(frozen['items'][0]['cumplimiento'],'10.00')
  self.m.meta_esperada=Decimal('99');self.m.save();self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).json()['data'],frozen)
  self.client.force_login(self.users['Consulta']);self.assertEqual(self.client.get('/api/operacion/actividades/').status_code,200);self.assertEqual(self.client.post('/api/captura/',{},content_type='application/json').status_code,403)
 def test_matriz_seis_roles_con_permisos_publicados(self):
  routes={'/api/cumplimiento/colectivo/?periodo='+str(self.p.pk):{'Administrador','Delegado'},'/api/ausencias/opciones/':{'Administrador','Delegado','Funcionario'},'/api/hitos/':{'Administrador','Delegado','Funcionario'},'/api/organizaciones/':{'Administrador','Delegado','Funcionario'},'/api/clasificacion-actividades/':{'Administrador','Delegado','Funcionario'},'/api/operacion/actividades/':set(self.users)}
  for label,user in self.users.items():
   self.client.force_login(user)
   for url,allowed in routes.items():
    with self.subTest(rol=label,url=url):self.assertEqual(self.client.get(url).status_code,200 if label in allowed else 403)
   for url,allowed in [('/api/hitos/',{'Administrador','Delegado'}),('/api/organizaciones/',{'Administrador','Delegado'}),('/api/ausencias/',{'Administrador','Delegado'}),('/api/clasificacion-actividades/'+str(self.i.pk)+'/',{'Administrador','Delegado'})]:
    with self.subTest(rol=label,escritura=url):self.assertEqual(self.send(url,{}).status_code,400 if label in allowed else 403)
 def test_administrador_sin_superusuario_gestiona_y_funcionario_no_escala(self):
  admin=self.users['Administrador'];self.assertFalse(admin.is_superuser);self.client.force_login(admin)
  row=self.post('/api/reclamos/',dict(clase='Felicitación',fecha='2026-02-10',vecino='Vecino ficticio',contacto='912345678',situacion='Respaldo formal ficticio',procedencia='Directa',destinatario='Delegación'));self.assertFalse(row['revision']['potencialmente_puntuable'])
  self.client.force_login(self.worker);self.assertEqual(self.send(f"/api/reclamos/{row['id']}/revision/",dict(_version=row['version'],decision='Validada',observacion='Intento sin permiso')).status_code,403)
 def test_permiso_de_equipo_no_suplanta_rol_restringido(self):
  for label in ['Coordinador','Verificador','Consulta','Funcionario']:
   user=self.users[label];user.rol.permisos+=['ausencias.ver','ausencias.ver_equipo','ausencias.gestionar'];user.rol.save();self.client.force_login(user)
   self.assertEqual(self.client.get('/api/cumplimiento/colectivo/',{'periodo':self.p.pk}).status_code,403)
   self.assertEqual(self.send('/api/ausencias/',{}).status_code,403)
