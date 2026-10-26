from .test_followup_assignment import FollowupAssignmentTests
from .models import Actividad,Compromiso,Vecino
import uuid

class TubeConnectionTests(FollowupAssignmentTests):
 def neighbor(self,**extra):
  return Vecino.objects.create(delegacion=self.d,nombre='Antonio QA',sector='Sector vecino',creado_por=self.u,clave_idempotencia=uuid.uuid4().hex,**extra)
 def test_neighbor_identity_persisted(self):
  n=self.neighbor();r=self.send('/api/operacion/compromisos/',{**self.commitment(vecino=n.pk),'solicitante':'Texto manipulado'})
  self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['vecino'],n.pk);self.assertEqual(Compromiso.objects.get().solicitante,n.nombre)
 def test_neighbor_from_other_delegation_rejected(self):
  n=self.neighbor();n.delegacion=self.other_d;n.save()
  self.assertEqual(self.send('/api/operacion/compromisos/',self.commitment(vecino=n.pk)).status_code,400);self.assertFalse(Compromiso.objects.exists())
 def test_existing_activity_links_once(self):
  r=self.send('/api/operacion/actividades/',self.activity());a=Actividad.objects.get(pk=r.json()['data']['id'])
  data=self.commitment(actividad_origen=a.pk);first=self.send('/api/operacion/compromisos/',data)
  self.assertEqual(first.status_code,201,first.content);a.refresh_from_db();self.assertEqual(a.compromiso_id,first.json()['data']['id']);self.assertEqual(Compromiso.objects.get().descripcion,a.solicitud)
  self.assertEqual(self.send('/api/operacion/compromisos/',data).status_code,409);self.assertEqual(Compromiso.objects.count(),1)
 def test_other_author_activity_not_linkable(self):
  r=self.send('/api/operacion/actividades/',self.activity());a=Actividad.objects.get(pk=r.json()['data']['id']);a.autor=self.peer;a.save()
  self.assertEqual(self.send('/api/operacion/compromisos/',self.commitment(actividad_origen=a.pk)).status_code,404)
 def test_source_search_is_scoped_and_marks_existing_followup(self):
  r=self.send('/api/operacion/actividades/',self.activity());a=Actividad.objects.get(pk=r.json()['data']['id'])
  self.send('/api/operacion/compromisos/',self.commitment(actividad_origen=a.pk))
  rows=self.client.get('/api/seguimiento/registros/',{'q':'Solicitud'}).json()['results'];self.assertEqual(len(rows),1);self.assertIsNotNone(rows[0]['compromiso'])
  a.autor=self.peer;a.save();self.assertEqual(self.client.get('/api/seguimiento/registros/',{'q':'Solicitud'}).json()['results'],[])
 def test_inactive_neighbor_rejected(self):
  n=self.neighbor(activo=False);self.assertEqual(self.send('/api/operacion/compromisos/',self.commitment(vecino=n.pk)).status_code,400)
 def test_capture_followup_carries_neighbor_reference(self):
  n=self.neighbor();payload=self.payload(nuevo_compromiso=self.follow());payload['actividad'].update(contacto=n.nombre);payload['vecino']=n.pk
  r=self.send('/api/captura/',payload);self.assertEqual(r.status_code,201,r.content);self.assertEqual(Compromiso.objects.get().vecino_id,n.pk)
 def test_invalid_deadline_does_not_link_or_create(self):
  r=self.send('/api/operacion/actividades/',self.activity());a=Actividad.objects.get(pk=r.json()['data']['id'])
  r=self.send('/api/operacion/compromisos/',{**self.commitment(actividad_origen=a.pk),'fecha_comprometida':'2000-01-01'})
  self.assertEqual(r.status_code,400);a.refresh_from_db();self.assertIsNone(a.compromiso_id);self.assertFalse(Compromiso.objects.exists())

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.test import TransactionTestCase,Client
from django.db import connection,close_old_connections
from unittest import skipUnless

@skipUnless(connection.vendor=='mysql','Requiere bloqueos de filas de MySQL')
class ConcurrentTubeConnectionTests(TransactionTestCase):
 setUp=FollowupAssignmentTests.setUp
 activity=FollowupAssignmentTests.activity
 payload=FollowupAssignmentTests.payload
 follow=FollowupAssignmentTests.follow
 commitment=FollowupAssignmentTests.commitment
 def test_two_requests_create_only_one_followup(self):
  r=self.client.post('/api/operacion/actividades/',self.activity(),content_type='application/json');a=Actividad.objects.get(pk=r.json()['data']['id']);barrier=Barrier(2)
  def create():
   close_old_connections();client=Client();client.force_login(self.u);barrier.wait(timeout=10)
   try:return client.post('/api/operacion/compromisos/',self.commitment(actividad_origen=a.pk),content_type='application/json').status_code
   finally:close_old_connections()
  with ThreadPoolExecutor(max_workers=2) as pool:codes=list(pool.map(lambda _:create(),range(2)))
  self.assertEqual(sorted(codes),[201,409]);self.assertEqual(Compromiso.objects.count(),1)
