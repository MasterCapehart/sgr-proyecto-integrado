from django.test import TestCase
from .models import Usuario,Rol,Cargo,ItemMeta,PeriodoGestion,ConfiguracionMeta

class WeightReviewTests(TestCase):
 def setUp(self):
  self.u=Usuario.objects.create_superuser('weight-admin','weights@example.test','LocalOnly!934')
  self.client.force_login(self.u)
  self.a=Cargo.objects.create(codigo='WA',nombre='Cargo A',area='Equipo')
  self.b=Cargo.objects.create(codigo='WB',nombre='Cargo B',area='Equipo')
  self.p=PeriodoGestion.objects.create(codigo='W26',nombre='Período ensayo',fecha_inicio='2026-07-01',fecha_fin='2026-09-30')
  self.i=ItemMeta.objects.create(codigo='WI',nombre='Actividad de ensayo')
 def meta(self,weight,cargo=None,item=None,**kw):
  return ConfiguracionMeta.objects.create(item=item or self.i,cargo=cargo,periodo_gestion=self.p,periodo=self.p.codigo,ponderacion=weight,meta_esperada=10,**kw)
 def result(self):
  r=self.client.get('/api/configuraciones-metas/revision-ponderaciones/',{'periodo':self.p.pk})
  self.assertEqual(r.status_code,200,r.content);return r.json()['data']
 def row(self,cargo):return next(r for r in self.result()['pautas'] if r['cargo']==cargo.pk)
 def test_general_fallback_specific_override_no_double_count(self):
  self.meta(20);self.meta(40,self.a)
  self.assertEqual(self.row(self.a)['suma'],'40.00')
  self.assertEqual(self.row(self.b)['suma'],'20.00')
 def test_partial_exact_and_excess_are_not_approval(self):
  m=self.meta('99.99',self.a)
  row=self.row(self.a);self.assertEqual(row['faltante'],'0.01');self.assertEqual(row['estado'],'Incompleta')
  m.ponderacion=100;m.save();row=self.row(self.a);self.assertEqual(row['estado'],'Suma 100 %');self.assertFalse(row['aprobada'])
  i=ItemMeta.objects.create(codigo='W2',nombre='Segunda');self.meta('0.01',self.a,item=i)
  row=self.row(self.a);self.assertEqual(row['exceso'],'0.01');self.assertEqual(row['estado'],'Excede 100 %')
 def test_inactive_and_reconciled_do_not_add(self):
  self.meta(30,self.a);i=ItemMeta.objects.create(codigo='W3',nombre='Tercera')
  self.meta(70,self.a,item=i,estado=False)
  self.assertEqual(self.row(self.a)['suma'],'30.00')
 def test_item_not_available_for_cargo_is_excluded(self):
  self.i.cargos.add(self.b);self.meta(20)
  self.assertEqual(self.row(self.a)['estado'],'Sin metas')
  self.assertEqual(self.row(self.b)['suma'],'20.00')
 def test_snapshot_uses_saved_weights_and_labels(self):
  self.p.cerrado=True;self.p.parametros_cierre={'metas':[dict(id=99,item=7,cargo=self.a.pk,cargo_nombre='Cargo guardado',ponderacion='85',estado=True)]};self.p.save()
  self.a.nombre='Nombre cambiado';self.a.save()
  row=self.row(self.a);self.assertEqual(row['cargo_nombre'],'Cargo guardado');self.assertEqual(row['suma'],'85.00')
 def test_closed_without_snapshot_does_not_reconstruct(self):
  self.meta(100,self.a);self.p.cerrado=True;self.p.save()
  result=self.result();self.assertEqual(result['pautas'],[]);self.assertEqual(result['fuente'],'Cierre sin parámetros de metas')
 def test_auth_permissions_invalid_period_and_read_only(self):
  path='/api/configuraciones-metas/revision-ponderaciones/'
  for value in ['abc','99999','','²']:
   self.assertEqual(self.client.get(path,{'periodo':value}).status_code,400)
  self.assertEqual(self.client.post(path,{},content_type='application/json').status_code,405)
  self.client.logout();self.assertEqual(self.client.get(path,{'periodo':self.p.pk}).status_code,401)
  reader=Usuario.objects.create_user('weight-reader',rol=Rol.objects.create(nombre='Consulta ponderaciones',permisos=[]));self.client.force_login(reader)
  self.assertEqual(self.client.get(path,{'periodo':self.p.pk}).status_code,403)
  reader.rol.permisos=['configuraciones-metas.ver'];reader.rol.save();self.assertEqual(self.client.get(path,{'periodo':self.p.pk}).status_code,200)

 def test_closed_malformed_snapshot_is_reported_without_server_error(self):
  self.p.cerrado=True;self.p.parametros_cierre={'metas':{'formato':'antiguo'}};self.p.save()
  result=self.result();self.assertEqual(result['pautas'],[]);self.assertEqual(result['fuente'],'Cierre sin parámetros de metas')
