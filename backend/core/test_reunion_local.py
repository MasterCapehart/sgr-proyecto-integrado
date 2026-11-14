from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from . import test_domain as domain_helpers
from .models import Compromiso,Actividad,Usuario,Rol

class ReunionLocalTests(domain_helpers.OperacionDominio):
 setUp=domain_helpers.OperacionDominio.setUp
 activity=domain_helpers.OperacionDominio.activity
 evidence=domain_helpers.OperacionDominio.evidence
 def reviewer(self):
  role=Rol.objects.create(nombre='Revisor acotado',permisos=['evidencias.ver','evidencias.revisar'])
  return Usuario.objects.create_user('revisor_acotado',delegacion=self.d,rol=role)
 def decide(self,e):return self.client.post(f"/api/operacion/evidencias/{e['id']}/revisar/",{'_version':e['version'],'decision':'Aprobada','observacion':'Respaldo comprobado'},content_type='application/json')
 def test_contexto_disponible_sin_ampliar_permiso_actividad(self):
  a=self.activity();e=self.evidence(a);self.client.force_login(self.reviewer())
  self.assertEqual(self.client.get(f"/api/operacion/actividades/{a['id']}/").status_code,403)
  data=self.client.get(f"/api/operacion/evidencias/{e['id']}/").json()['data']
  self.assertEqual(data['actividad_contexto']['solicitud'],a['solicitud']);self.assertEqual(data['actividad_contexto']['accion'],a['accion']);self.assertEqual(data['actividad_autor'],self.u.pk)
  self.assertNotIn('telefono',data['actividad_contexto']);self.assertNotIn('contacto',data['actividad_contexto'])
 def test_revision_parcial_y_final_no_cierran_compromiso(self):
  a=self.activity();e1=self.evidence(a);e2=self.evidence(a)
  c=Compromiso.objects.create(delegacion=self.d,autor=self.u,responsable=self.u,descripcion='Pendiente de ejecutar',sector='Centro',fecha_comprometida=timezone.localdate(),origen='Interno');Actividad.objects.filter(pk=a['id']).update(compromiso=c)
  self.client.force_login(self.reviewer());r=self.decide(e1);self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(r.json()['data']['actividad_contexto']['estado'],'Pendiente');self.assertEqual(r.json()['data']['revision_resumen']['pendientes'],1)
  r=self.decide(e2);self.assertEqual(r.status_code,200);self.assertEqual(r.json()['data']['actividad_contexto']['estado'],'Validada');c.refresh_from_db();self.assertEqual(c.estado,'Pendiente')
 def test_orden_prioriza_vencidos_y_deja_realizados_al_final(self):
  today=timezone.localdate();items=[]
  for name,status,delta in [('Cerrado','Realizado',-10),('En curso','En proceso',2),('Pendiente','Pendiente',2),('Ingresado','Ingresado',3),('Vencido','En proceso',-1)]:
   items.append(Compromiso.objects.create(autor=self.u,delegacion=self.d,responsable=self.u,descripcion=name,estado=status,fecha_comprometida=today+timedelta(days=delta),sector='Centro',origen='Interno'))
  r=self.client.get('/api/operacion/compromisos/',{'page_size':2});self.assertEqual([o['descripcion'] for o in r.json()['results']],['Vencido','Ingresado'])
  full=self.client.get('/api/operacion/compromisos/',{'page_size':100}).json()['results'];self.assertEqual([o['descripcion'] for o in full],['Vencido','Ingresado','Pendiente','En curso','Cerrado'])
