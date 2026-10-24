"""Contraste con lotes CAL-A..F, PDF de segunda evaluación, página 7.

Pruebas del comportamiento existente: no incorporan puntaje integral ni reglas
pendientes. CAL-B usa el tope posterior del 120 %, no el antiguo 150 %.
"""
from datetime import date
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from . import test_performance as fixtures
from .models import ItemMeta, ConfiguracionMeta, Compromiso
from .collective import consolidate, status
from .kpis import resource_kpis

class CalculosFuentesTests(TestCase):
 setUp=fixtures.PerformanceTests.setUp
 send=fixtures.PerformanceTests.send
 calendar=fixtures.PerformanceTests.calendar
 activity=fixtures.PerformanceTests.activity
 summary=fixtures.PerformanceTests.summary
 def configure(self,first_count):
  self.m.meta_esperada=10;self.m.ponderacion=40;self.m.save()
  second=ItemMeta.objects.create(codigo='CAL-I02',nombre='Ítem segundo del lote CAL')
  ConfiguracionMeta.objects.create(item=second,periodo_gestion=self.p,periodo=self.p.codigo,meta_esperada=20,ponderacion=60)
  for _ in range(first_count):self.activity()
  for _ in range(10):self.activity(item=second)
  return self.summary()
 def test_cal_a_aportes_32_30_total_62(self):
  summary=self.configure(8);rows={r['codigo']:r for r in summary['metas']}
  self.assertEqual(rows[self.i.codigo]['cumplimiento'],'80.00')
  self.assertEqual(rows[self.i.codigo]['aporte_ponderado'],'32.00')
  self.assertEqual(rows['CAL-I02']['cumplimiento'],'50.00')
  self.assertEqual(rows['CAL-I02']['aporte_ponderado'],'30.00')
  self.assertEqual(sum(Decimal(r['aporte_ponderado']) for r in rows.values()),Decimal('62'))
  self.assertEqual(consolidate([summary])['personas'][0]['cumplimiento'],'62.00')
 def test_cal_b_actualizado_120_aporte_48_total_78(self):
  summary=self.configure(20);row=next(r for r in summary['metas'] if r['item']==self.i.pk)
  self.assertEqual(row['total_registrado'],20)
  self.assertEqual(row['unidades_reconocidas'],'12.00')
  self.assertEqual(row['cumplimiento'],'120.00')
  self.assertEqual(row['aporte_ponderado'],'48.00')
  self.assertEqual(sum(Decimal(r['aporte_ponderado']) for r in summary['metas']),Decimal('78'))
 def test_cal_c_conteos_de_compromisos_no_duplican_total(self):
  for i,state in enumerate(['Realizado']*8+['Pendiente','En proceso']):
   Compromiso.objects.create(autor=self.worker,delegacion=self.d,responsable=self.worker,descripcion='Compromiso CAL ficticio',fecha_comprometida=date(2026,2,10),estado=state,folio=f'CAL-{i}')
  data=resource_kpis(Compromiso.objects.all(),'compromisos')
  cards={r['key']:r['value'] for r in data['cards']}
  self.assertEqual(cards['total'],10);self.assertEqual(cards['realizados'],8);self.assertEqual(cards['en_curso'],2)
  # El KPI entrega conteos, no un campo de cumplimiento porcentual del tubo.
  self.assertNotIn('cumplimiento',data)
 def test_cal_d_calendario_explicito_inclusivo_y_limites(self):
  self.p.fecha_inicio=date(2026,10,1);self.p.fecha_fin=date(2026,10,30);self.p.save()
  from .models import CalendarioFuncionario
  calendar=CalendarioFuncionario.objects.get(pk=self.cal['id']);calendar.semana=['Completa']*7;calendar.save()
  for day,expected in [(date(2026,10,15),'50.00'),(date(2026,11,1),'100.00'),(date(2026,9,30),None)]:
   with self.subTest(day=day),patch('core.absences.timezone.localdate',return_value=day):
    result=self.summary();self.assertEqual(result['dias_previstos'],'30.00')
    self.assertEqual(result['objetivo_al_dia'],expected)
  # Antes del inicio el sistema mantiene estado neutral, en lugar del 0 % del lote.
 def test_cal_e_limites_con_precision_antes_de_redondear(self):
  for value,color in [('29.99','Rojo'),('30','Naranjo'),('49.99','Naranjo'),('50','Verde'),('29.999','Rojo')]:
   with self.subTest(value=value):self.assertEqual(status(Decimal(value),Decimal('50')),color)
 def test_pauta_parcial_indice_normalizado_no_es_total_integral(self):
  self.activity();summary=self.summary();row=summary['metas'][0]
  self.assertEqual(row['aporte_ponderado'],'2.00')
  self.assertEqual(consolidate([summary])['personas'][0]['cumplimiento'],'10.00')
  # Pauta parcial peso20: índice normalizado10 % distinto del aporte2 puntos.
