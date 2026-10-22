import uuid
from django.test import TestCase
from . import test_unified_capture as helpers
from .models import Usuario,Rol,Compromiso,Actividad

class MilestoneTests(TestCase):
 setUp=helpers.UnifiedCaptureTests.setUp
 def send(self,url,data,method='post'):return getattr(self.client,method)(url,data,content_type='application/json')
 def payload(self,**kw):return dict(nombre='Entrega navideña ficticia',descripcion='Planificación QA',fecha_inicio='2026-12-20',fecha_termino='2026-12-21',territorio='Sector QA',responsables=[self.u.pk],recursos=[dict(descripcion='Cajas',cantidad='100',unidad='unidades')],recurrente=True,periodicidad='Anual',clave_idempotencia=uuid.uuid4().hex,**kw)
 def hito(self,**kw):
  r=self.send('/api/hitos/',self.payload(**kw));self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def task(self,h,**kw):
  r=self.send(f'/api/hitos/{h["id"]}/tareas/',dict(nombre='Organizar entrega',descripcion='Coordinar puntos de entrega',responsable=self.u.pk,fecha_limite='2026-12-19',**kw));self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def worker(self):
  role=Rol.objects.create(nombre='Funcionario Hitos QA',permisos=['hitos.ver','hitos.avanzar','compromisos.ver','compromisos.editar'])
  return Usuario.objects.create_user('funcionario_hito',delegacion=self.d,rol=role)
 def test_creacion_recursos_y_reintento(self):
  data=self.payload();a=self.send('/api/hitos/',data);self.assertEqual(a.status_code,201,a.content);b=self.send('/api/hitos/',data);self.assertEqual(b.status_code,200,b.content);self.assertEqual(a.json()['data']['id'],b.json()['data']['id']);self.assertEqual(a.json()['data']['recursos'][0]['cantidad'],'100');self.assertFalse(Actividad.objects.exists())
  data['nombre']='Otro';self.assertEqual(self.send('/api/hitos/',data).status_code,409)
 def test_validaciones_no_dejan_datos_parciales(self):
  for key,value in [('fecha_termino','2026-12-01'),('responsables',[self.other.pk]),('recursos',[dict(descripcion='X',cantidad='-1',unidad='u')]),('periodicidad',''),('delegacion',self.other_d.pk)]:
   data=self.payload();data[key]=value;self.assertEqual(self.send('/api/hitos/',data).status_code,400)
 def test_sin_sesion_y_funcionario_no_crean(self):
  self.client.logout();self.assertEqual(self.client.get('/api/hitos/').status_code,401);self.client.force_login(self.worker());self.assertEqual(self.send('/api/hitos/',self.payload()).status_code,403)
 def test_funcionario_solo_propias_tareas_y_avances(self):
  w=self.worker();h=self.hito();r=self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],responsables=[self.u.pk,w.pk]),'patch');self.assertEqual(r.status_code,200,r.content)
  mine=self.task(h);data=dict(nombre='Preparar cajas',descripcion='Clasificar',responsable=w.pk,fecha_limite='2026-12-19');r=self.send(f'/api/hitos/{h["id"]}/tareas/',data);self.assertEqual(r.status_code,201,r.content);own=r.json()['data'];self.client.force_login(w)
  detail=self.client.get(f'/api/hitos/{h["id"]}/').json()['data'];self.assertEqual([t['id'] for t in detail['tareas']],[own['id']]);self.assertEqual(self.send(f'/api/hitos/{h["id"]}/tareas/',data).status_code,403)
  self.assertEqual(self.send(f'/api/hitos/tareas/{mine["id"]}/avances/',dict(_version=mine['version'],porcentaje=50,observacion='Avance')).status_code,404)
  r=self.send(f'/api/hitos/tareas/{own["id"]}/avances/',dict(_version=own['version'],porcentaje=50,observacion='Cajas preparadas'));self.assertEqual(r.status_code,200,r.content);self.assertEqual(r.json()['data']['avances'][0]['observacion'],'Cajas preparadas')
  self.assertEqual(self.send(f'/api/hitos/tareas/{own["id"]}/avances/',dict(_version=own['version'],porcentaje=60,observacion='Antiguo')).status_code,409)
 def test_aislamiento_y_responsables_activos(self):
  h=self.hito();s=self.client.session;s['delegacion_activa']=self.other_d.pk;s.save();self.assertEqual(self.client.get(f'/api/hitos/{h["id"]}/').status_code,404);self.assertEqual(self.client.get('/api/hitos/').json()['results'],[])
 def test_tubo_unico_interno_sin_actividad_duplicada(self):
  h=self.hito();t=self.task(h);url=f'/api/hitos/tareas/{t["id"]}/tubo/';a=self.send(url,dict(_version=t['version']));self.assertEqual(a.status_code,201,a.content);b=self.send(url,dict(_version=t['version']));self.assertEqual(b.status_code,200,b.content);self.assertEqual(Compromiso.objects.count(),1);self.assertEqual(Compromiso.objects.get().origen,'Interno');self.assertFalse(Actividad.objects.exists())
  c=Compromiso.objects.get();r=self.send(f'/api/operacion/compromisos/{c.pk}/',dict(_version=c.version,origen='Externo',observacion='Cambio'),'patch');self.assertEqual(r.status_code,400,r.content)
 def test_cierre_bloquea_avances_y_recurrencia_independiente(self):
  h=self.hito();t=self.task(h);self.assertEqual(self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],estado='Finalizado'),'patch').status_code,400)
  r=self.send(f'/api/hitos/tareas/{t["id"]}/avances/',dict(_version=t['version'],porcentaje=100,observacion='Terminada'));self.assertEqual(r.status_code,200,r.content)
  r=self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],estado='Finalizado'),'patch');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(self.send(f'/api/hitos/tareas/{t["id"]}/avances/',dict(_version=r.json()['data']['tareas'][0]['version'],porcentaje=80,observacion='Cambio')).status_code,400)
  new=self.hito(hito_anterior=h['id']);self.assertEqual(new['hito_anterior'],h['id']);self.assertEqual(new['tareas'],[])
 def test_hito_version_y_tarea_validan_ediciones(self):
  h=self.hito();t=self.task(h)
  self.assertEqual(self.send(f'/api/hitos/{h["id"]}/',dict(_version=0,nombre='Otro'),'patch').status_code,409)
  self.assertEqual(self.send(f'/api/hitos/tareas/{t["id"]}/',dict(_version=t['version'],responsable=self.other.pk),'patch').status_code,400)
  for value in [-1,101,True,'50']:
   self.assertEqual(self.send(f'/api/hitos/tareas/{t["id"]}/avances/',dict(_version=t['version'],porcentaje=value,observacion='Inválido')).status_code,400)
 def test_persona_no_asignada_no_ve_evento(self):
  h=self.hito();self.client.force_login(self.worker());self.assertEqual(self.client.get('/api/hitos/').json()['results'],[]);self.assertEqual(self.client.get(f'/api/hitos/{h["id"]}/').status_code,404)
 def test_no_retira_responsable_con_tarea_y_interno_no_cambia(self):
  h=self.hito();t=self.task(h);w=self.worker()
  self.assertEqual(self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],responsables=[w.pk]),'patch').status_code,400)
  self.send(f'/api/hitos/tareas/{t["id"]}/tubo/',dict(_version=t['version']));c=Compromiso.objects.get()
  origins=self.client.get(f'/api/operacion/compromisos/{c.pk}/origenes/');self.assertEqual(origins.status_code,200,origins.content);self.assertEqual(origins.json()['results'][0]['tipo'],'hito')
 def test_funcionario_actualiza_estado_tubo_no_reasigna_y_gestor_sincroniza(self):
  w=self.worker();h=self.hito();self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],responsables=[self.u.pk,w.pk]),'patch')
  r=self.send(f'/api/hitos/{h["id"]}/tareas/',dict(nombre='Tarea',descripcion='Preparación',responsable=w.pk,fecha_limite='2026-12-19'));self.assertEqual(r.status_code,201,r.content);t=r.json()['data'];self.send(f'/api/hitos/tareas/{t["id"]}/tubo/',dict(_version=t['version']));c=Compromiso.objects.get()
  self.client.force_login(w);url=f'/api/operacion/compromisos/{c.pk}/';r=self.send(url,dict(_version=c.version,estado='En proceso',observacion='Iniciada'),'patch');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(self.send(url,dict(_version=r.json()['data']['version'],responsable=self.u.pk,observacion='Reasignar'),'patch').status_code,400)
  self.client.force_login(self.u);c.refresh_from_db();r=self.send(url,dict(_version=c.version,responsable=self.u.pk,fecha_comprometida='2026-12-18',observacion='Reasignación autorizada'),'patch');self.assertEqual(r.status_code,200,r.content)
  detail=self.client.get(f'/api/hitos/{h["id"]}/').json()['data']['tareas'][0];self.assertEqual(detail['responsable'],self.u.pk);self.assertEqual(detail['fecha_limite'],'2026-12-18');self.assertEqual(detail['estado_tubo'],'En proceso')
 def test_cancelado_no_admite_nuevas_tareas_o_edicion_tubo(self):
  h=self.hito();t=self.task(h);self.send(f'/api/hitos/tareas/{t["id"]}/tubo/',dict(_version=t['version']));r=self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],estado='Cancelado'),'patch');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(self.send(f'/api/hitos/{h["id"]}/tareas/',dict(nombre='Nueva')).status_code,400)
  c=Compromiso.objects.get();self.assertEqual(self.send(f'/api/operacion/compromisos/{c.pk}/',dict(_version=c.version,observacion='Cambio',estado='En proceso'),'patch').status_code,400)
 def test_no_crea_tubo_con_plazo_anterior_a_su_solicitud(self):
  h=self.hito();r=self.send(f'/api/hitos/{h["id"]}/tareas/',dict(nombre='Preparación anterior',descripcion='Tarea pendiente',responsable=self.u.pk,fecha_limite='2020-01-01'));self.assertEqual(r.status_code,201,r.content);t=r.json()['data']
  r=self.send(f'/api/hitos/tareas/{t["id"]}/tubo/',dict(_version=t['version']));self.assertEqual(r.status_code,400,r.content);self.assertFalse(Compromiso.objects.exists())
 def test_responsable_inactivado_permite_reasignacion_sin_perder_historial(self):
  w=self.worker();data=self.payload();data['responsables']=[w.pk];r=self.send('/api/hitos/',data);self.assertEqual(r.status_code,201,r.content);h=r.json()['data']
  r=self.send(f'/api/hitos/{h["id"]}/tareas/',dict(nombre='Tarea',descripcion='Preparación',responsable=w.pk,fecha_limite='2026-12-19'));self.assertEqual(r.status_code,201,r.content);t=r.json()['data'];w.is_active=False;w.save()
  r=self.send(f'/api/hitos/{h["id"]}/',dict(_version=h['version'],responsables=[w.pk,self.u.pk]),'patch');self.assertEqual(r.status_code,200,r.content)
  r=self.send(f'/api/hitos/tareas/{t["id"]}/',dict(_version=t['version'],responsable=self.u.pk),'patch');self.assertEqual(r.status_code,200,r.content)
