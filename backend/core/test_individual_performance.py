"""Personal targets feed the existing validated-evidence calculation."""
from decimal import Decimal
from django.test import TestCase
from . import test_performance as performance
from .goal_models import AsignacionMeta
from .models import CalendarioFuncionario, ConfiguracionMeta, Delegacion, ItemMeta


class IndividualPerformanceTests(TestCase):
    setUp = performance.PerformanceTests.setUp
    send = performance.PerformanceTests.send
    calendar = performance.PerformanceTests.calendar
    absence = performance.PerformanceTests.absence
    summary = performance.PerformanceTests.summary
    activity = performance.PerformanceTests.activity
    row = performance.PerformanceTests.row

    def assignment(self, **extra):
        return AsignacionMeta.objects.create(funcionario=self.worker, item=self.i,
            periodo=self.p, delegacion=self.d, cantidad_objetivo=20,
            ponderacion=35, autor=self.u, **extra)

    def test_personal_target_and_weight_override_role_default(self):
        assignment = self.assignment()
        self.activity(asignacion_meta=assignment)
        self.activity()  # Historical item-only records cannot claim a new assignment.
        row = self.row()
        self.assertEqual(row['asignacion_meta'], assignment.pk)
        self.assertEqual(row['meta_original'], '20.00')
        self.assertEqual(row['ponderacion'], '35.00')
        self.assertEqual(row['total_registrado'], 1)
        self.assertEqual(row['cumplimiento'], '5.00')
        self.assertEqual(row['aporte_ponderado'], '1.75')

    def test_personal_target_still_requires_validated_evidence(self):
        assignment = self.assignment()
        self.activity(asignacion_meta=assignment, estado='Pendiente')
        activity = self.activity(asignacion_meta=assignment)
        activity.evidencias.get().revisiones.all().delete()
        self.assertEqual(self.row()['validas'], 0)
        self.assertEqual(self.row()['cumplimiento'], '0.00')

    def test_personal_assignment_without_role_configuration_is_included(self):
        item = ItemMeta.objects.create(codigo='PERSONAL', nombre='Personal')
        assignment = AsignacionMeta.objects.create(funcionario=self.worker, item=item,
            periodo=self.p, delegacion=self.d, cantidad_objetivo=5,
            ponderacion=15, autor=self.u)
        self.activity(item=item, asignacion_meta=assignment)
        row = next(m for m in self.summary()['metas'] if m['item'] == item.pk)
        self.assertEqual(row['cumplimiento'], '20.00')
        self.assertFalse(row['prorrateable'])

    def test_inactive_or_other_delegation_assignment_does_not_override(self):
        assignment = self.assignment(estado=False)
        self.assertIsNone(self.row()['asignacion_meta'])
        assignment.estado = True
        assignment.delegacion = Delegacion.objects.create(codigo='OTHER-PERSONAL', nombre='Otra')
        assignment.save()
        self.assertIsNone(self.row()['asignacion_meta'])

    def test_close_preserves_personal_target_and_result(self):
        assignment = self.assignment()
        self.activity(asignacion_meta=assignment)
        response = self.send(f'/api/periodos/{self.p.pk}/cerrar/',
            dict(_version=self.p.version, motivo='Conservar asignación individual'))
        self.assertEqual(response.status_code, 200, response.content)
        assignment.cantidad_objetivo = Decimal('100')
        assignment.save()
        self.assertEqual(self.row()['meta_original'], '20.00')
        self.assertEqual(self.row()['cumplimiento'], '5.00')

    def test_missing_calendar_does_not_invent_personal_performance(self):
        self.assignment()
        CalendarioFuncionario.objects.filter(pk=self.cal['id']).delete()
        row = self.row()
        self.assertEqual(row['meta_original'], '20.00')
        self.assertIsNone(row['cumplimiento'])
        self.assertEqual(row['semaforo'], 'Sin calendario')

    def test_personal_plan_does_not_merge_unassigned_role_defaults(self):
        assignment = self.assignment()
        assignment.ponderacion = 100
        assignment.save()
        item = ItemMeta.objects.create(codigo='ROLEONLY', nombre='Solo cargo')
        ConfiguracionMeta.objects.create(item=item, periodo_gestion=self.p,
            periodo=self.p.codigo, meta_esperada=10, ponderacion=50)
        rows = self.summary()['metas']
        self.assertEqual([m['asignacion_meta'] for m in rows], [assignment.pk])
        self.assertEqual(sum(Decimal(m['ponderacion']) for m in rows), Decimal('100'))

    def test_catalogue_deactivation_does_not_erase_an_assigned_plan(self):
        assignment = self.assignment()
        self.i.estado = False
        self.i.save()
        self.p.estado = False
        self.p.save()
        row = self.row()
        self.assertEqual(row['asignacion_meta'], assignment.pk)
        self.assertEqual(row['meta_original'], '20.00')
