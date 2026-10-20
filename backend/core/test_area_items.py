from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from .models import Cargo, ItemMeta, Usuario, Delegacion
from .area_catalog import REFERENCE
from .area_items import configure
from .excel_support import items_for

class AreaItemsTests(TestCase):
 def setUp(self):
  self.d=Delegacion.objects.create(codigo='AI',nombre='QA')
  self.u=Usuario.objects.create_superuser('areas_items',password='QA-local-937!',delegacion=self.d)
  self.r=RequestFactory().post('/catalogo-local/');self.r.user=self.u;self.r.session={}
  for row in REFERENCE:Cargo.objects.create(**{k:row[k] for k in ['codigo','nombre','area','planilla']})
 def test_preview_no_escribe_y_aplicar_repite_sin_duplicar(self):
  self.assertEqual(configure(self.r)['relations'],73);self.assertEqual(ItemMeta.objects.count(),0)
  configure(self.r,apply=True);self.assertEqual(ItemMeta.objects.count(),22)
  self.assertEqual(ItemMeta.cargos.through.objects.count(),73)
  configure(self.r,apply=True);self.assertEqual(ItemMeta.objects.count(),22);self.assertEqual(ItemMeta.cargos.through.objects.count(),73)
 def test_reutiliza_item_conserva_asociaciones_y_historicos(self):
  old=Cargo.objects.create(codigo='OLD',nombre='Anterior',planilla='AP_ADM')
  i=ItemMeta.objects.create(codigo='ANTERIOR',nombre='EMERGENCIA',unidad_medida='Cantidad');i.cargos.add(old)
  configure(self.r,apply=True);i.refresh_from_db();self.assertEqual(i.codigo,'ANTERIOR');self.assertTrue(i.cargos.filter(pk=old.pk).exists());self.assertEqual(i.cargos.count(),13)
 def test_conflicto_unidad_aborta_sin_cambios_parciales(self):
  ItemMeta.objects.create(codigo='OLD',nombre='EMERGENCIA',unidad_medida='Porcentaje')
  with self.assertRaises(ValidationError):configure(self.r,apply=True)
  self.assertEqual(ItemMeta.objects.count(),1);self.assertEqual(ItemMeta.cargos.through.objects.count(),0)
 def test_faltan_areas_aborta(self):
  Cargo.objects.get(nombre='GESTOR SOCIAL 5').delete()
  with self.assertRaises(ValidationError):configure(self.r,apply=True)
  self.assertEqual(ItemMeta.objects.count(),0)
 def test_planillas_filtran_items_por_area_y_conservan_generales(self):
  configure(self.r,apply=True)
  general=ItemMeta.objects.create(codigo='GENERAL',nombre='General autorizado')
  self.u.is_superuser=False
  for name,expected,not_expected in [('GESTOR SOCIAL 2','ENTREGA BENEFICIO','INFORMES PERSONAL'),('TERRITORIAL OO.CC. 3','VISITAS, REUNIONES CON ORGANIZACIONES','ENTREGA BENEFICIO'),('COOR SERV. COMU','INFORMES PERSONAL','INFORME DE INVENTARIOS')]:
   self.u.cargo=Cargo.objects.get(nombre=name)
   names=set(items_for(self.u).values_list('nombre',flat=True));self.assertIn(expected,names);self.assertNotIn(not_expected,names);self.assertIn(general.nombre,names)
 def test_items_calculados_no_se_ofrecen_y_no_cambia_usuarios(self):
  configure(self.r,apply=True);self.u.refresh_from_db();self.assertIsNone(self.u.cargo_id)
  self.assertFalse(ItemMeta.objects.filter(nombre__icontains='TUBO').exists())
  self.assertTrue(ItemMeta.objects.filter(nombre='VISITAS, REUNIONES CON ORGANIZACIONES').exists())
  self.assertFalse(ItemMeta.objects.filter(nombre__in=['VISITAS','REUNIONES CON ORGANIZACIONES']).exists())

 def test_api_rechaza_item_de_otra_area(self):
  from .models import Rol
  from django.utils import timezone
  configure(self.r,apply=True)
  self.u.is_superuser=False;self.u.cargo=Cargo.objects.get(nombre='TERRITORIAL OO.CC. 2')
  self.u.rol=Rol.objects.create(nombre='Funcionario ítems',permisos=['actividades.ver','actividades.crear']);self.u.save()
  self.client.force_login(self.u)
  options=self.client.get('/api/operacion/opciones/');self.assertEqual(options.status_code,200)
  names={i['nombre'] for i in options.json()['items']};self.assertIn('CONFORMACION DE ORGANIZACIONES',names);self.assertNotIn('ENTREGA BENEFICIO',names)
  data={'fecha':str(timezone.localdate()),'solicitud':'Prueba local','accion':'Prueba','contacto':'Persona ficticia','telefono':'912345678','sector':'QA','item':ItemMeta.objects.get(nombre='ENTREGA BENEFICIO').pk}
  self.assertEqual(self.client.post('/api/operacion/actividades/',data,content_type='application/json').status_code,400)
  data['item']=ItemMeta.objects.get(nombre='CONFORMACION DE ORGANIZACIONES').pk
  self.assertEqual(self.client.post('/api/operacion/actividades/',data,content_type='application/json').status_code,201)

 def test_unidad_legacy_uno_conserva_codigo_y_unidad(self):
  item=ItemMeta.objects.create(codigo='ITEM-001',nombre='ATENCION DE USUARIO TELEFONO Y PRESENCIAL',unidad_medida='1')
  configure(self.r,apply=True)
  item.refresh_from_db();self.assertEqual(item.unidad_medida,'1');self.assertEqual(item.codigo,'ITEM-001');self.assertEqual(item.cargos.count(),5)
