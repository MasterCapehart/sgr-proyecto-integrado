from django.test import TestCase
from .models import Usuario, Delegacion, Rol, ItemMeta, TipoAtencion, SubAtencion

class AcercamientoExcel(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='EX',nombre='Excel prueba')
  self.u=Usuario.objects.create_superuser('excel','excel@example.test','ClaveExcel!3783',delegacion=self.d)
  self.client.force_login(self.u)
  self.item=ItemMeta.objects.create(codigo='EX',nombre='Gestión general')
  self.tipo=TipoAtencion.objects.create(codigo='EX',nombre='Social')
  self.sub=SubAtencion.objects.create(codigo='EX',nombre='Orientación',tipo_atencion=self.tipo)
 def post(self,url,data):return self.client.post(url,data,content_type='application/json')
 def activity(self):
  r=self.post('/api/operacion/actividades/',{'fecha':'2026-10-15','solicitud':'Problema','accion':'Gestión','contacto':'Vecino','telefono':'+56912345678','sector':'Centro','item':self.item.pk});self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def attention(self,**extra):
  data={'solicitante':'Persona ficticia','tipo_atencion':self.tipo.pk,'sub_atencion':self.sub.pk,'descripcion':'Orientación social','caso_social':'EX-CASO',**extra}
  r=self.post('/api/atenciones/',data);self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_cargo_distinto_de_rol(self):
  r=self.post('/api/cargos/',{'codigo':'SOC','nombre':'Gestor Social','area':'Gestión social'});self.assertEqual(r.status_code,201,r.content)
  c=r.json()['data'];role=Rol.objects.create(nombre='Rol cargo',permisos=['atenciones.ver'])
  user=Usuario.objects.create_user('cargo_prueba',email='cargo_prueba@example.test',first_name='Persona',rol=role,delegacion=self.d);user.delegaciones.add(self.d)
  r=self.client.patch(f'/api/usuarios/{user.pk}/',{'_version':user.version,'cargo':c['id']},content_type='application/json');self.assertEqual(r.status_code,200,r.content)
  user.refresh_from_db();self.assertEqual(user.cargo_id,c['id']);self.assertEqual(user.rol_id,role.pk);self.assertEqual(user.rol.permisos,['atenciones.ver'])
 def test_items_por_cargo_y_sin_escalamiento(self):
  from .models import Cargo
  social=Cargo.objects.create(codigo='SOC',nombre='Social',area='Social');seg=Cargo.objects.create(codigo='SEG',nombre='Seguridad',area='Seguridad')
  restricted=ItemMeta.objects.create(codigo='SEG',nombre='Inspección');restricted.cargos.add(seg)
  role=Rol.objects.create(nombre='Funcionario Excel',permisos=['actividades.ver','actividades.crear'])
  user=Usuario.objects.create_user('social_excel',delegacion=self.d,cargo=social,rol=role)
  self.client.force_login(user);opts=self.client.get('/api/operacion/opciones/').json();self.assertNotIn(restricted.pk,[i['id'] for i in opts['items']]);self.assertIn(self.item.pk,[i['id'] for i in opts['items']])
  a=self.activity();self.assertEqual(a['cargo'],social.pk);self.assertEqual(user.rol_id,role.pk)
 def test_derivacion_con_version_e_historial(self):
  a=self.activity();url=f"/api/operacion/actividades/{a['id']}/derivacion/"
  r=self.post(url,{'_version':a['version'],'destino':'Alumbrado público','motivo':'Evaluar luminaria','estado':'Pendiente'});self.assertEqual(r.status_code,200,r.content)
  a=r.json()['data'];self.assertEqual(a['derivado_a'],'Alumbrado público');self.assertEqual(len(a['derivaciones']),1)
  self.assertEqual(self.post(url,{'_version':1,'destino':'Otro','motivo':'Obsoleto','estado':'Resuelta'}).status_code,409)
 def test_fecha_solicitud_independiente_y_mes(self):
  r=self.post('/api/operacion/compromisos/',{'descripcion':'Agenda','solicitante':'Vecina','sector':'Centro','responsable':self.u.pk,'fecha_solicitud':'2026-10-01','fecha_comprometida':'2026-11-01','area_apoyo':'Operaciones','origen':'Externo'});self.assertEqual(r.status_code,201,r.content)
  self.assertEqual(r.json()['data']['fecha_solicitud'],'2026-10-01');self.assertEqual(r.json()['data']['mes_compromiso'],'11')
 def test_expediente_tres_gestiones_con_fechas(self):
  self.attention(telefono_solicitante='+56912345678',requiere_visita=True,fecha_visita='2026-10-20',gestion_realizada='Orientación inicial')
  self.attention(fecha_entrega_informe='2026-10-22',gestion_realizada='Entrega de informe')
  self.attention(fecha_entrega_beneficio='2026-10-25',gestion_realizada='Entrega de beneficio')
  r=self.client.get('/api/casos-sociales/EX-CASO/');self.assertEqual(r.status_code,200,r.content);data=r.json()['data'];self.assertEqual(len(data['gestiones']),3);self.assertEqual(data['gestiones'][0]['fecha_visita'],'2026-10-20')
 def test_expediente_fuera_de_delegacion(self):
  self.attention();other=Delegacion.objects.create(codigo='OT',nombre='Otra Excel');self.u.delegacion=other;self.u.save();self.client.force_login(self.u)
  self.assertEqual(self.client.get('/api/casos-sociales/EX-CASO/').status_code,404)
 def test_visita_incoherente_rechazada(self):
  r=self.post('/api/atenciones/',{'solicitante':'Persona','tipo_atencion':self.tipo.pk,'sub_atencion':self.sub.pk,'descripcion':'Prueba','requiere_visita':False,'fecha_visita':'2026-10-20'});self.assertEqual(r.status_code,400)
 def test_actividad_muestra_respaldo_y_tubo(self):
  a=self.activity();self.assertEqual(a['evidencias_actuales'],[]);self.assertEqual(a['ingreso_tubo'],'No')
 def test_reintento_con_run_formateado_no_duplica(self):
  data={'solicitante':'Persona','tipo_atencion':self.tipo.pk,'sub_atencion':self.sub.pk,'descripcion':'Prueba','rut_solicitante':'12.345.678-5','clave_idempotencia':'excel-reintento'}
  first=self.post('/api/atenciones/',data);self.assertEqual(first.status_code,201,first.content)
  replay=self.post('/api/atenciones/',data);self.assertEqual(replay.status_code,200,replay.content);self.assertEqual(first.json()['data']['id'],replay.json()['data']['id'])
 def test_filtro_por_columna_de_gestiones(self):
  a=self.activity();r=self.client.get('/api/operacion/actividades/?col_contacto=Vecino');self.assertEqual(r.status_code,200,r.content);self.assertEqual(r.json()['count'],1)
  self.assertEqual(self.client.get('/api/operacion/actividades/?col_contacto=Ausente').json()['count'],0)
 def test_expediente_unico_y_contacto_informado_en_segunda_gestion(self):
  self.attention()
  self.attention(solicitante='PERSONA   FICTICIA',rut_solicitante='12345678-5',telefono_solicitante='+56912345678')
  listing=self.client.get('/api/casos-sociales/').json();self.assertEqual(listing['count'],1)
  detail=self.client.get('/api/casos-sociales/EX-CASO/').json()['data'];self.assertEqual(detail['rut_solicitante'],'12345678-5');self.assertEqual(detail['telefono_solicitante'],'+56912345678')
 def test_visita_ausente_no_se_inventa_como_no(self):
  a=self.attention();self.assertIsNone(a['requiere_visita'])
 def test_sin_cargo_solo_items_generales(self):
  from .models import Cargo
  cargo=Cargo.objects.create(codigo='EXC',nombre='Exclusivo',area='Seguridad');restricted=ItemMeta.objects.create(codigo='EXC',nombre='Ítem exclusivo');restricted.cargos.add(cargo)
  role=Rol.objects.create(nombre='Sin cargo Excel',permisos=['actividades.ver','actividades.crear']);user=Usuario.objects.create_user('sin_cargo_excel',rol=role,delegacion=self.d);self.client.force_login(user)
  ids=[i['id'] for i in self.client.get('/api/operacion/opciones/').json()['items']];self.assertIn(self.item.pk,ids);self.assertNotIn(restricted.pk,ids)
 def test_reintento_invalido_devuelve_400_no_500(self):
  data={'solicitante':'Persona','tipo_atencion':self.tipo.pk,'sub_atencion':self.sub.pk,'descripcion':'Prueba','clave_idempotencia':'excel-invalido'}
  self.assertEqual(self.post('/api/atenciones/',data).status_code,201)
  self.client.raise_request_exception=False
  for field,value in [('fecha_visita','no-es-fecha'),('rut_solicitante','incorrecto'),('requiere_visita','si')]:
   r=self.post('/api/atenciones/',{**data,field:value});self.assertEqual(r.status_code,400,r.content[:200])
 def test_json_invalido_atencion_devuelve_400(self):
  self.client.raise_request_exception=False
  r=self.client.post('/api/atenciones/',data='{invalido',content_type='application/json');self.assertEqual(r.status_code,400,r.content[:200])
 def test_filtro_funcionario_por_nombre_completo_y_usuario(self):
  self.u.first_name='Daniel';self.u.last_name='Prueba';self.u.save();self.activity()
  for text in ['Daniel Prueba','excel']:
   r=self.client.get('/api/operacion/actividades/',{'col_autor_nombre':text});self.assertEqual(r.json()['count'],1,r.content)
 def test_fecha_actividad_respeta_dia_local_de_la_serena(self):
  from unittest.mock import patch
  from datetime import datetime, timezone as dt_timezone
  # 01:00 UTC del 16 todavía es día 15 en La Serena.
  with patch('django.utils.timezone.now',return_value=datetime(2026,10,16,1,tzinfo=dt_timezone.utc)):
   r=self.post('/api/operacion/actividades/',{'fecha':'2026-10-16','solicitud':'Prueba','accion':'Prueba','contacto':'Vecino','telefono':'+56912345678','sector':'Centro','item':self.item.pk});self.assertEqual(r.status_code,400,r.content)
