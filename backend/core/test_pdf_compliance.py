from .test_corrections_suite import CorrectionsSuiteTests
from .models import Actividad,Compromiso
from django.utils import timezone
from datetime import date,timedelta

class PdfComplianceAudit(CorrectionsSuiteTests):
    def activity(self,state='Aprobada y pondera'):
        return Actividad.objects.create(autor=self.func_d1,delegacion=self.d1,item=self.item2,fecha=date(2026,2,10),solicitud='Caso académico',accion='Gestión',sector='Centro',estado=state)
    def derive(self,a):
        self.client.force_login(self.func_d1)
        return self.client.post(f'/api/operacion/actividades/{a.pk}/derivacion/',{'_version':a.version,'destino':'Unidad de prueba','motivo':'Seguimiento de prueba','estado':'Pendiente'},content_type='application/json')
    def test_approved_activity_cannot_be_modified_by_derivation(self):
        r=self.derive(self.activity())
        self.assertIn(r.status_code,[400,403,409],'PDF §15: actividad aprobada no admite modificaciones; derivación fue aceptada')
    def test_closed_period_cannot_be_modified_by_derivation(self):
        a=self.activity('Pendiente');self.periodo.cerrado=True;self.periodo.save()
        r=self.derive(a)
        self.assertIn(r.status_code,[400,403,409],'PDF §15: cierre no puede eludirse derivando la actividad')
    def test_realizado_not_overdue_in_tube_kpi(self):
        self.r_func.permisos=self.r_func.permisos+['compromisos.ver'];self.r_func.save()
        Compromiso.objects.create(autor=self.func_d1,delegacion=self.d1,responsable=self.func_d1,descripcion='Caso académico realizado',sector='Centro',origen='Interno',estado='Realizado',fecha_comprometida=timezone.localdate()-timedelta(days=1))
        self.client.force_login(self.func_d1)
        r=self.client.get('/api/operacion/compromisos/')
        self.assertEqual(r.status_code,200,r.content)
        overdue=next(x['value'] for x in r.json()['kpis']['cards'] if x['key']=='vencidos')
        self.assertEqual(overdue,0,'Realizado excluido del filtro de vencidos pero incluido en su KPI')

    def test_dashboard_personal_indicadores_minimos(self):
        self.activity('Borrador')
        self.client.force_login(self.func_d1)
        r = self.client.get('/api/mi-progreso/')
        self.assertEqual(r.status_code, 200)
        data = r.json()['data']
        self.assertIn('ultimo_registro', data)
        self.assertIn('promedio_diario', data)
        self.assertIn('reclamos_felicitaciones', data)
        self.assertIn('hitos_proximos', data)
        self.assertIsNotNone(data['ultimo_registro'])

    def test_dashboard_colectivo_indicadores_y_export(self):
        self.client.force_login(self.admin)
        # Test JSON
        r = self.client.get(f'/api/cumplimiento/colectivo/?periodo={self.periodo.pk}')
        self.assertEqual(r.status_code, 200)
        data = r.json()['data']
        self.assertIn('metas_menor_cumplimiento', data)
        self.assertIn('hitos_proximos', data)
        self.assertIn('evolucion_trimestral', data)
        # Test Export
        r_exp = self.client.get(f'/api/cumplimiento/colectivo/?periodo={self.periodo.pk}&export=1')
        self.assertEqual(r_exp.status_code, 200)
        self.assertIn('application/vnd.openxmlformats', r_exp['Content-Type'])

    def test_expediente_social_campos_y_cierre(self):
        from .models import Atencion, TipoAtencion, SubAtencion
        tipo = TipoAtencion.objects.create(codigo='SOC1', nombre='Asistencia Social')
        sub = SubAtencion.objects.create(codigo='SUB1', nombre='Subsidio', tipo_atencion=tipo)
        atencion = Atencion.objects.create(
            folio='CASO-SOC-01-G1', solicitante='Juan Perez', rut_solicitante='12.345.678-5',
            tipo_atencion=tipo, sub_atencion=sub, descripcion='Solicitud inicial',
            delegacion=self.d1, usuario=self.func_d1, caso_social='CASO-SOC-01', numero_gestion=1,
            fecha_visita_programada=date(2026, 1, 10), fecha_visita_realizada=date(2026, 1, 12),
            fecha_entrega_informe=date(2026, 1, 15), fecha_entrega_beneficio=date(2026, 1, 20)
        )
        self.client.force_login(self.func_d1)
        r = self.client.get('/api/casos-sociales/')
        self.assertEqual(r.status_code, 200)
        body = r.json()
        results = body.get('results') if 'results' in body else body.get('data', {}).get('results', [])
        caso = next(x for x in results if x['caso_social'] == 'CASO-SOC-01')
        self.assertEqual(caso['estado_general'], 'Cerrado')
        self.assertEqual(caso['resultado'], 'Beneficio entregado')
        self.assertIn('fecha_atencion', caso)
        self.assertEqual(caso['tiempos']['programacion_visita'], 2)
        self.assertEqual(caso['tiempos']['visita_informe'], 3)
        self.assertIsNotNone(caso['tiempos']['atencion_beneficio'])

    def test_evolution_excludes_evidence_only_validated_activity(self):
        Actividad.objects.create(autor=self.func_d1,delegacion=self.d1,item=self.item2,fecha=date(2026,2,10),solicitud='Prueba',accion='Gestión',sector='Centro',estado='Validada')
        self.client.force_login(self.admin)
        r=self.client.get(f'/api/cumplimiento/colectivo/?periodo={self.periodo.pk}')
        self.assertEqual(r.status_code,200,r.content)
        total=sum(x['actividades_ponderadas'] for x in r.json()['data']['evolucion_trimestral'])
        self.assertEqual(total,0,'PDF §13: la evolución ponderada incluye Validada sin decisión explícita de ponderación')

    def test_compliance_export_includes_generation_timestamp(self):
        from openpyxl import load_workbook
        from io import BytesIO
        self.client.force_login(self.admin)
        r=self.client.get(f'/api/cumplimiento/colectivo/?periodo={self.periodo.pk}&export=1')
        self.assertEqual(r.status_code,200,r.content)
        w=load_workbook(BytesIO(r.content),data_only=True)
        values=[str(v).casefold() for row in w.active.iter_rows(values_only=True) for v in row if v is not None]
        self.assertTrue(any('generado' in v or 'generación' in v or 'generacion' in v for v in values),'PDF §16: XLSX no informa fecha y hora de generación')

    def test_expediente_social_cierre_sin_beneficio(self):
        from .models import Atencion, TipoAtencion, SubAtencion
        tipo = TipoAtencion.objects.create(codigo='SOC2', nombre='Asistencia Social 2')
        sub = SubAtencion.objects.create(codigo='SUB2', nombre='Orientación', tipo_atencion=tipo)
        atencion = Atencion.objects.create(
            folio='CASO-SOC-02-G1', solicitante='Maria Soto', rut_solicitante='15.678.901-2',
            tipo_atencion=tipo, sub_atencion=sub, descripcion='Orientación inicial',
            delegacion=self.d1, usuario=self.func_d1, caso_social='CASO-SOC-02', numero_gestion=1,
            tipo_gestion='Cierre de caso: orientación completada sin beneficio',
            gestion_realizada='Usuario derivado a red de salud. Caso social cerrado sin entrega de beneficio.',
            fecha_visita_realizada=date(2026, 1, 15)
        )
        self.client.force_login(self.func_d1)
        r = self.client.get('/api/casos-sociales/')
        self.assertEqual(r.status_code, 200)
        body = r.json()
        results = body.get('results') if 'results' in body else body.get('data', {}).get('results', [])
        caso = next(x for x in results if x['caso_social'] == 'CASO-SOC-02')
        self.assertEqual(caso['estado_general'], 'Cerrado')
        self.assertIn('Cierre', caso['resultado'])
        self.assertEqual(caso['fecha_cierre'], '2026-01-15')
