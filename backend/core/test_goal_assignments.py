from django.test import TestCase
from . import test_unified_capture as helpers
from .models import PeriodoGestion, Usuario, Rol

class GoalAssignmentTests(TestCase):
 def setUp(self):
  helpers.UnifiedCaptureTests.setUp(self)
  self.p=PeriodoGestion.objects.create(codigo='T126',nombre='Trimestre 1 QA',anio=2026,numero=1,fecha_inicio='2026-01-01',fecha_fin='2026-03-31')
 def send(self,data,pk=None):return getattr(self.client,'patch' if pk else 'post')('/api/asignaciones-metas/'+(f'{pk}/' if pk else ''),data,content_type='application/json')
 def payload(self,**kw):return dict(funcionario=self.u.pk,item=self.i.pk,periodo=self.p.pk,cantidad_objetivo='80',ponderacion='20',observacion='Plan individual',estado=True,**kw)
 def create(self,data=None):
  r=self.send(data or self.payload());self.assertEqual(r.status_code,201,r.content);return r.json()['data']
 def test_partial_weight_and_individual_targets(self):
  a=self.create();self.assertEqual(a['ponderacion'],'20.00')
  w=Usuario.objects.create_user('otro',delegacion=self.d)
  d=self.payload();d.update(funcionario=w.pk,cantidad_objetivo='90',ponderacion='25');b=self.create(d);self.assertNotEqual(a['cantidad_objetivo'],b['cantidad_objetivo'])
 def test_sum_above_100_rejected_and_inactive_excluded(self):
  from .models import ItemMeta
  self.create();i=ItemMeta.objects.create(codigo='I2',nombre='Otra meta');d=self.payload();d.update(item=i.pk,ponderacion='81');self.assertEqual(self.send(d).status_code,400)
  d['estado']=False;a=self.create(d);self.assertEqual(self.send(dict(_version=a['version'],estado=True),a['id']).status_code,400)
 def test_closed_period_version_and_history(self):
  a=self.create();self.assertEqual(self.send(dict(_version=0,observacion='Otro'),a['id']).status_code,409)
  self.p.cerrado=True;self.p.save();self.assertEqual(self.send(dict(_version=a['version'],estado=False),a['id']).status_code,400)
 def test_invalid_target_scope_duplicate_and_unknown_fields(self):
  for k,v in [('cantidad_objetivo','0'),('cantidad_objetivo','NaN'),('ponderacion','101'),('funcionario',self.other.pk),('estado','true'),('cargo',1)]:
   d=self.payload();d[k]=v;self.assertEqual(self.send(d).status_code,400)
  self.create();self.assertEqual(self.send(self.payload()).status_code,409)
 def test_read_scope_and_manager_only(self):
  a=self.create();role=Rol.objects.create(nombre='Funcionario metas QA',permisos=['asignaciones-metas.ver','asignaciones-metas.crear'])
  w=Usuario.objects.create_user('lector',delegacion=self.d,rol=role);self.client.force_login(w)
  self.assertEqual(self.client.get('/api/asignaciones-metas/').json()['results'],[]);self.assertEqual(self.client.get(f'/api/asignaciones-metas/{a["id"]}/').status_code,404);self.assertEqual(self.send(self.payload()).status_code,403)
 def test_quarter_dates(self):
  self.p.fecha_fin='2026-04-01';self.p.save();self.assertEqual(self.send(self.payload()).status_code,400)
 def test_unauthenticated(self):
  self.client.logout();self.assertEqual(self.client.get('/api/asignaciones-metas/').status_code,401)
 def test_exact_100_and_deactivation_release_weight(self):
  from .models import ItemMeta
  d=self.payload();d['ponderacion']='100';a=self.create(d)
  i=ItemMeta.objects.create(codigo='II',nombre='Meta secundaria');d.update(item=i.pk,ponderacion='0.01');self.assertEqual(self.send(d).status_code,400)
  self.assertEqual(self.send(dict(_version=a['version'],estado=False),a['id']).status_code,200)
  self.create(d)
 def test_audit_snapshot_and_identity_immutable(self):
  from .models import EventoLocal
  a=self.create();self.i.nombre='Nombre posterior';self.i.save()
  current=self.client.get(f'/api/asignaciones-metas/{a["id"]}/').json()['data'];self.assertEqual(current['item_nombre'],'Ítem QA')
  self.assertEqual(self.send(dict(_version=a['version'],funcionario=self.other.pk),a['id']).status_code,400)
  r=self.send(dict(_version=a['version'],cantidad_objetivo='90',observacion='Ajuste'),a['id']);self.assertEqual(r.status_code,200,r.content)
  events=EventoLocal.objects.filter(recurso='asignaciones-metas',registro=a['id']);self.assertEqual(events.count(),2);self.assertEqual(events.last().antes['cantidad_objetivo'],'80.00')
 def test_invalid_decimal_boolean_and_precision(self):
  for k,v in [('cantidad_objetivo',True),('cantidad_objetivo','1.001'),('ponderacion','Infinity'),('ponderacion',True)]:
   d=self.payload();d[k]=v;self.assertEqual(self.send(d).status_code,400)
 def test_csrf_enforced(self):
  from django.test import Client
  c=Client(enforce_csrf_checks=True);c.force_login(self.u)
  self.assertEqual(c.post('/api/asignaciones-metas/',self.payload(),content_type='application/json').status_code,403)
 def test_same_person_weight_shared_across_delegations(self):
  from .models import ItemMeta
  self.u.delegaciones.add(self.other_d);d=self.payload();d['ponderacion']='90';self.create(d)
  session=self.client.session;session['delegacion_activa']=self.other_d.pk;session.save()
  i=ItemMeta.objects.create(codigo='CROSS',nombre='Meta otra delegación');d.update(item=i.pk,ponderacion='11');self.assertEqual(self.send(d).status_code,400)

 def test_inactive_person_allows_deactivation_for_history(self):
  a=self.create();self.u.is_active=False;self.u.save()
  admin=Usuario.objects.create_superuser('replacement_admin',delegacion=self.d);self.client.force_login(admin)
  r=self.send(dict(_version=a['version'],estado=False),a['id']);self.assertEqual(r.status_code,200,r.content)

 def test_bind_activity_accepts_iso_date_and_rejects_invalid(self):
  from .models import Actividad
  from .goal_api import bind_activity
  from django.core.exceptions import ValidationError
  from django.db import transaction
  a=self.create()
  activity=Actividad(autor=self.u,item=self.i,delegacion=self.d,fecha='2026-02-15')
  with transaction.atomic():bind_activity(activity,a['id'])
  self.assertEqual(activity.asignacion_meta_id,a['id'])
  activity.fecha='not-a-date'
  with transaction.atomic(),self.assertRaises(ValidationError):bind_activity(activity,a['id'])

 def test_available_assignments_filter_date_and_closed(self):
  self.create()
  url=f'/api/asignaciones-metas/?funcionario={self.u.pk}&disponibles=1&fecha='
  self.assertEqual(len(self.client.get(url+'2026-02-15').json()['results']),1)
  self.assertEqual(self.client.get(url+'2026-04-01').json()['results'],[])
  self.assertEqual(self.client.get(url+'bad').status_code,400)
  self.p.cerrado=True;self.p.save();self.assertEqual(self.client.get(url+'2026-02-15').json()['results'],[])

from django.test import TransactionTestCase
from django.db import connections
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

class GoalConcurrencyTests(TransactionTestCase):
 def test_concurrent_creations_cannot_exceed_100(self):
  from .models import Delegacion, ItemMeta
  from .goal_models import AsignacionMeta
  from django.test import Client
  d=Delegacion.objects.create(codigo='LOCK',nombre='Delegación concurrencia')
  u=Usuario.objects.create_superuser('gestor_lock',delegacion=d)
  p=PeriodoGestion.objects.create(codigo='LOCKT',nombre='Trimestre concurrencia',anio=2026,numero=1,fecha_inicio='2026-01-01',fecha_fin='2026-03-31')
  items=[ItemMeta.objects.create(codigo=f'LOCK{i}',nombre=f'Meta concurrente {i}') for i in range(2)]
  clients=[Client(),Client()]
  for c in clients:c.force_login(u)
  barrier=Barrier(2)
  def create(index):
   try:
    barrier.wait(timeout=10)
    r=clients[index].post('/api/asignaciones-metas/',dict(funcionario=u.pk,item=items[index].pk,periodo=p.pk,cantidad_objetivo='10',ponderacion='60',estado=True),content_type='application/json')
    return r.status_code
   finally:connections.close_all()
  with ThreadPoolExecutor(max_workers=2) as pool:codes=list(pool.map(create,[0,1]))
  self.assertEqual(sorted(codes),[201,400]);self.assertEqual(AsignacionMeta.objects.count(),1)

class IncrementCatalogTests(TestCase):
 setUp=helpers.UnifiedCaptureTests.setUp
 def test_goal_catalog_fields_and_quarter_dates(self):
  r=self.client.patch(f'/api/items-metas/{self.i.pk}/',dict(_version=self.i.version,tipo='Gestión social',requiere_evidencia=True),content_type='application/json');self.assertEqual(r.status_code,200,r.content);self.i.refresh_from_db();self.assertTrue(self.i.requiere_evidencia)
  p=PeriodoGestion.objects.create(codigo='CAT26',nombre='Calendario QA',fecha_inicio='2026-01-01',fecha_fin='2026-03-31')
  url=f'/api/periodos/{p.pk}/'
  r=self.client.patch(url,dict(_version=p.version,anio=2026,numero=2),content_type='application/json');self.assertEqual(r.status_code,400,r.content)
  r=self.client.patch(url,dict(_version=p.version,anio=2026,numero=1),content_type='application/json');self.assertEqual(r.status_code,200,r.content)
 def test_delegation_delegate_must_belong_to_scope(self):
  url=f'/api/delegaciones/{self.d.pk}/'
  r=self.client.patch(url,dict(_version=self.d.version,delegado=self.other.pk),content_type='application/json');self.assertEqual(r.status_code,400,r.content)
  r=self.client.patch(url,dict(_version=self.d.version,delegado=self.u.pk),content_type='application/json');self.assertEqual(r.status_code,200,r.content)
