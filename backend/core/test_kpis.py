from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from .models import Delegacion, Usuario, Rol, ItemMeta, Actividad, Compromiso

class IndicadoresOperativos(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='KPI',nombre='KPI local')
  self.other=Delegacion.objects.create(codigo='KPI2',nombre='Otra KPI')
  self.u=Usuario.objects.create_superuser('kpi','kpi@example.test','ClaveLocal!937',delegacion=self.d)
  self.item=ItemMeta.objects.create(codigo='KPI',nombre='Ítem KPI');self.client.force_login(self.u)
 def activity(self,**kwargs):
  return Actividad.objects.create(delegacion=self.d,autor=self.u,item=self.item,fecha=timezone.localdate(),solicitud='Prueba KPI',accion='Acción',contacto='QA',telefono='912345678',sector='Centro',**kwargs)
 def commitment(self,**kwargs):
  return Compromiso.objects.create(delegacion=self.d,autor=self.u,responsable=self.u,descripcion='Compromiso KPI',solicitante='QA',sector='Centro',area_apoyo='QA',origen='Interno',**kwargs)
 def values(self,data):return {x['key']:x['value'] for x in data['cards']}
 def test_listado_agrega_todas_las_paginas_y_respeta_filtro(self):
  self.activity(estado='Validada');self.activity(estado='Validada');self.activity(estado='Borrador')
  r=self.client.get('/api/operacion/actividades/?page_size=1');self.assertEqual(r.status_code,200)
  self.assertEqual(len(r.json()['results']),1);self.assertEqual(self.values(r.json()['kpis'])['total'],3)
  filtered=self.client.get('/api/operacion/actividades/?estado=Validada').json();self.assertEqual(self.values(filtered['kpis'])['total'],2);self.assertEqual(self.values(filtered['kpis'])['validadas'],2)
 def test_home_respeta_delegacion_y_permiso(self):
  self.activity();Actividad.objects.create(delegacion=self.other,autor=self.u,item=self.item,fecha=timezone.localdate(),solicitud='Oculta',accion='QA',contacto='QA',telefono='912345678',sector='Otro')
  data=self.client.get('/api/indicadores/').json()['data'];self.assertEqual(self.values(data)['actividades'],1)
  role=Rol.objects.create(nombre='Solo actividades KPI',permisos=['actividades.ver'])
  self.u.is_superuser=False;self.u.rol=role;self.u.save();data=self.client.get('/api/indicadores/').json()['data'];self.assertEqual(set(self.values(data)),{'actividades'})
 def test_home_sin_sesion_rechaza(self):
  self.client.logout();self.assertEqual(self.client.get('/api/indicadores/').status_code,401)
 def test_compromiso_realizado_no_cuenta_como_vencido(self):
  day=timezone.localdate()-timedelta(days=2)
  self.commitment(fecha_comprometida=day,estado='Realizado');self.commitment(fecha_comprometida=day,estado='Ingresado');self.commitment(fecha_comprometida=timezone.localdate(),estado='Ingresado')
  kpis=self.client.get('/api/operacion/compromisos/').json()['kpis'];self.assertEqual(self.values(kpis)['vencidos'],1);self.assertEqual(self.values(kpis)['realizados'],1)
 def test_scope_propio_no_cuenta_actividades_de_otro(self):
  self.activity();role=Rol.objects.create(nombre='Personal KPI',permisos=['actividades.ver']);other=Usuario.objects.create_user('otro_kpi',rol=role,delegacion=self.d);self.client.force_login(other)
  self.assertEqual(self.values(self.client.get('/api/operacion/actividades/').json()['kpis'])['total'],0)
 def test_atenciones_no_duplican_casos_y_excluyen_otra_delegacion(self):
  from .models import TipoAtencion,SubAtencion,Atencion
  tipo=TipoAtencion.objects.create(codigo='KPI',nombre='Tipo KPI');sub=SubAtencion.objects.create(codigo='KPI',nombre='Sub KPI',tipo_atencion=tipo)
  for n,d,caso in [(1,self.d,'CASO-KPI'),(2,self.d,'CASO-KPI'),(3,self.other,None)]:
   Atencion.objects.create(folio=f'KPI-{n}',solicitante='QA',tipo_atencion=tipo,sub_atencion=sub,descripcion='QA',delegacion=d,usuario=self.u,caso_social=caso,numero_gestion=n)
  values=self.values(self.client.get('/api/atenciones/').json()['kpis']);self.assertEqual(values['total'],2);self.assertEqual(values['casos'],1);self.assertEqual(values['mes'],2)
 def test_evidencias_cuentan_estados_y_filtran_sin_paginacion(self):
  from .models import Evidencia
  a=self.activity()
  for state in ['Pendiente','Aprobada','Corrección','Rechazada','Anulada']:
   Evidencia.objects.create(actividad=a,autor=self.u,delegacion=self.d,archivo='prueba-no-fisica',nombre_archivo='QA.pdf',tipo_mime='application/pdf',tamano=12,sha256='a'*64,descripcion='QA',estado=state)
  values=self.values(self.client.get('/api/operacion/evidencias/?page_size=1').json()['kpis']);self.assertEqual(values['total'],5);self.assertEqual(values['pendientes'],1);self.assertEqual(values['aprobadas'],1);self.assertEqual(values['devueltas'],2)
  values=self.values(self.client.get('/api/operacion/evidencias/?estado=Anulada').json()['kpis']);self.assertEqual(values['total'],1);self.assertEqual(values['pendientes'],0)
 def test_inicio_incluye_compromiso_asignado_y_excluye_ajeno(self):
  role=Rol.objects.create(nombre='Responsable KPI',permisos=['compromisos.ver']);other=Usuario.objects.create_user('asignado_kpi',rol=role,delegacion=self.d)
  c=self.commitment(fecha_comprometida=timezone.localdate()-timedelta(days=1));c.responsable=other;c.save()
  self.commitment(fecha_comprometida=timezone.localdate()-timedelta(days=1));self.client.force_login(other)
  values=self.values(self.client.get('/api/indicadores/').json()['data']);self.assertEqual(values,{'abiertos':1,'vencidos':1})
