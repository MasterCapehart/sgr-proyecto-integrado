from django.test import TestCase
from django.utils import timezone
from . import test_kpis as helpers
from .models import Usuario,Rol,Compromiso

class TubeProgressTests(TestCase):
 setUp=helpers.IndicadoresOperativos.setUp
 commitment=helpers.IndicadoresOperativos.commitment
 def result(self,**filters):
  r=self.client.get('/api/operacion/compromisos/',filters);self.assertEqual(r.status_code,200,r.content);return r.json()
 def fill(self):
  for state in ['Realizado']*8+['Pendiente','En proceso']:self.commitment(fecha_comprometida=timezone.localdate(),estado=state)
 def test_cal_c_eight_of_ten_no_pagination_duplication(self):
  self.fill();r=self.result(page_size=1);self.assertEqual(len(r['results']),1)
  progress=r['kpis']['completion'];self.assertEqual(progress['total'],10);self.assertEqual(progress['realizados'],8);self.assertEqual(progress['por_completar'],2);self.assertEqual(progress['porcentaje'],'80.00')
 def test_empty_is_neutral(self):
  progress=self.result()['kpis']['completion'];self.assertEqual(progress['total'],0);self.assertIsNone(progress['porcentaje']);self.assertIsNone(progress['porcentaje_exacto'])
 def test_ingresado_in_denominator_and_filters_explicit(self):
  self.fill();self.commitment(fecha_comprometida=timezone.localdate(),estado='Ingresado')
  progress=self.result()['kpis']['completion'];self.assertEqual(progress['total'],11);self.assertEqual(progress['por_completar'],3);self.assertEqual(progress['porcentaje'],'72.73')
  filtered=self.result(estado='Realizado')['kpis']['completion'];self.assertEqual(filtered['total'],8);self.assertEqual(filtered['porcentaje'],'100.00')
  filtered=self.result(estado='Pendiente')['kpis']['completion'];self.assertEqual(filtered['total'],1);self.assertEqual(filtered['porcentaje'],'0.00')
 def test_scope_personal_and_other_delegation(self):
  self.fill();role=Rol.objects.create(nombre='Personal tubo',permisos=['compromisos.ver']);reader=Usuario.objects.create_user('tube-reader',rol=role,delegacion=self.d)
  c=self.commitment(fecha_comprometida=timezone.localdate(),estado='Realizado');c.responsable=reader;c.save()
  c=self.commitment(fecha_comprometida=timezone.localdate(),estado='Pendiente');c.responsable=reader;c.save()
  Compromiso.objects.create(delegacion=self.other,autor=reader,responsable=reader,descripcion='Ajeno',sector='Otro',origen='Interno',fecha_comprometida=timezone.localdate(),estado='Realizado')
  self.client.force_login(reader);progress=self.result()['kpis']['completion'];self.assertEqual(progress['total'],2);self.assertEqual(progress['porcentaje'],'50.00')
 def test_fractional_percentage_preserves_precision_and_updates(self):
  first=self.commitment(fecha_comprometida=timezone.localdate(),estado='Realizado')
  pending=self.commitment(fecha_comprometida=timezone.localdate(),estado='Ingresado')
  self.commitment(fecha_comprometida=timezone.localdate(),estado='Pendiente')
  progress=self.result()['kpis']['completion'];self.assertEqual(progress['porcentaje'],'33.33');self.assertTrue(progress['porcentaje_exacto'].startswith('33.3333'))
  pending.estado='Realizado';pending.save();self.assertEqual(self.result()['kpis']['completion']['porcentaje'],'66.67')
  first.estado='En proceso';first.save();self.assertEqual(self.result()['kpis']['completion']['porcentaje'],'33.33')
