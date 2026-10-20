from django.test import TestCase
from django.utils import timezone
from .models import Delegacion,Usuario,TipoAtencion,SubAtencion,Cargo,ItemMeta,Actividad

class AutomaticCodesTests(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='OLD',nombre='QA códigos')
  self.u=Usuario.objects.create_superuser('codigos_qa',password='LocalQA!937',delegacion=self.d);self.client.force_login(self.u)
 def post(self,path,data):return self.client.post('/api/'+path+'/',data,content_type='application/json')
 def test_seis_catalogos_se_crean_sin_codigo(self):
  t=TipoAtencion.objects.create(codigo='T',nombre='Tipo anterior')
  for resource,data,prefix in [('delegaciones',{'nombre':'Nueva delegación','direccion':'QA','comuna':'La Serena'},'DEL'),('cargos',{'nombre':'Cargo nuevo','area':'QA','planilla':'AP_ADM'},'CAR'),('items-metas',{'nombre':'Ítem nuevo','unidad_medida':'Cantidad'},'ITM'),('tipos-atencion',{'nombre':'Tipo nuevo'},'TIP'),('subatenciones',{'nombre':'Sub nueva','tipo_atencion':t.pk},'SUB'),('periodos',{'nombre':'Período nuevo','fecha_inicio':'2027-01-01','fecha_fin':'2027-03-31'},'PER')]:
   r=self.post(resource,data);self.assertEqual(r.status_code,201,r.content);self.assertRegex(r.json()['data']['codigo'],r'^'+prefix+r'-\d{6,}$')
 def test_codigo_anterior_no_se_reescribe_y_un_nuevo_blanco_se_genera(self):
  r=self.post('delegaciones',{'nombre':'Otra','codigo':''});self.assertEqual(r.status_code,201,r.content)
  r=self.client.patch('/api/delegaciones/'+str(self.d.pk)+'/',{'nombre':'Renombrada','_version':self.d.version},content_type='application/json');self.assertEqual(r.status_code,200,r.content);self.d.refresh_from_db();self.assertEqual(self.d.codigo,'OLD')
 def test_actividad_codigo_por_area_fecha_y_pk_estable(self):
  c=Cargo.objects.create(codigo='C',nombre='GESTOR SOCIAL 3',area='SOCIAL',planilla='G_SOC');self.u.cargo=c;self.u.save()
  i=ItemMeta.objects.create(codigo='I',nombre='QA')
  r=self.post('operacion/actividades',{'fecha':'2026-10-20','solicitud':'QA','accion':'QA','contacto':'Persona ficticia','telefono':'912345678','sector':'QA','item':i.pk})
  self.assertEqual(r.status_code,201,r.content);obj=r.json()['data'];self.assertRegex(obj['codigo'],r'^SCO3-20261020-\d{6,}$')
  r=self.client.patch('/api/operacion/actividades/'+str(obj['id'])+'/',{'_version':obj['version'],'fecha':'2026-10-19'},content_type='application/json');self.assertEqual(r.status_code,200,r.content);self.assertEqual(r.json()['data']['codigo'],obj['codigo'])
 def test_compromiso_codigo_foto_y_folio_automaticos(self):
  r=self.post('operacion/compromisos',{'descripcion':'QA','solicitante':'Persona ficticia','sector':'QA','responsable':self.u.pk,'fecha_comprometida':str(timezone.localdate()),'area_apoyo':'QA','origen':'Interno'})
  self.assertEqual(r.status_code,201,r.content);data=r.json()['data'];self.assertTrue(data['folio'].startswith('TUB-'));self.assertTrue(data['codigo_verificacion_foto'].startswith('FOTO-'))
 def attention(self,**extra):
  t,_=TipoAtencion.objects.get_or_create(codigo='SOC',defaults={'nombre':'Social'});s,_=SubAtencion.objects.get_or_create(codigo='SOC',defaults={'nombre':'Orientación','tipo_atencion':t})
  return self.post('atenciones',dict(solicitante='Persona ficticia',descripcion='QA',tipo_atencion=t.pk,sub_atencion=s.pk,**extra))
 def test_caso_auto_continuidad_y_reintento(self):
  r=self.attention(nuevo_caso=True,caso_social='',clave_idempotencia='NUEVO');self.assertEqual(r.status_code,201,r.content);data=r.json()['data'];self.assertRegex(data['caso_social'],r'^CS-\d{8}-\d{6,}$')
  repeat=self.attention(nuevo_caso=True,caso_social='',clave_idempotencia='NUEVO');self.assertEqual(repeat.status_code,200,repeat.content);self.assertEqual(repeat.json()['data']['id'],data['id'])
  for n in [2,3]:
   r=self.attention(caso_social=data['caso_social']);self.assertEqual(r.status_code,201,r.content);self.assertEqual(r.json()['data']['numero_gestion'],n)
  self.assertEqual(self.attention(caso_social=data['caso_social']).status_code,409)
 def test_atencion_simple_no_abre_caso_y_flag_invalido_rechazado(self):
  r=self.attention();self.assertEqual(r.status_code,201,r.content);self.assertFalse(r.json()['data']['caso_social']);self.assertTrue(r.json()['data']['folio'].startswith('AT-'))
  self.assertEqual(self.attention(nuevo_caso='si').status_code,400)

 def test_codigo_heredado_ocupado_no_colisiona(self):
  next_id=Delegacion.objects.order_by('-pk').first().pk+2
  old=Delegacion.objects.create(codigo=f'DEL-{next_id:06d}',nombre='Código reservado anterior')
  r=self.post('delegaciones',{'nombre':'Sin colisión','direccion':'QA','comuna':'La Serena'})
  self.assertEqual(r.status_code,201,r.content);self.assertNotEqual(r.json()['data']['codigo'],old.codigo)
  old.refresh_from_db();self.assertEqual(old.codigo,f'DEL-{next_id:06d}')
 def test_codigo_invalido_no_se_convierte_en_automatico(self):
  self.assertEqual(self.post('tipos-atencion',{'codigo':0,'nombre':'Inválido'}).status_code,400)

from django.test import TransactionTestCase, Client
from django.db import close_old_connections
from concurrent.futures import ThreadPoolExecutor

class ConcurrentAutomaticCodesTests(TransactionTestCase):
 def test_altas_simultaneas_tienen_codigos_distintos(self):
  d=Delegacion.objects.create(codigo='CONC',nombre='QA concurrencia códigos')
  user=Usuario.objects.create_superuser('concurrent_codes',password='LocalQA!937',delegacion=d)
  def create(index):
   close_old_connections()
   try:
    client=Client();client.force_login(Usuario.objects.get(pk=user.pk))
    response=client.post('/api/cargos/',{'nombre':f'Cargo simultáneo {index}','area':'QA','planilla':'AP_ADM'},content_type='application/json')
    return response.status_code,response.json()
   finally:close_old_connections()
  with ThreadPoolExecutor(max_workers=4) as executor:results=list(executor.map(create,range(4)))
  for status,data in results:self.assertEqual(status,201,data)
  self.assertEqual(len({data['data']['codigo'] for _,data in results}),4)
