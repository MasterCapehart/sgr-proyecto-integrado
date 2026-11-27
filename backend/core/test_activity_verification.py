"""Pruebas exhaustivas para verificación explícita de 6 estados (DF10-DF14) y cálculo 120% (DF15-DF16)."""
from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Usuario, Delegacion, ItemMeta, Rol, Actividad, RevisionActividad, EventoLocal, PeriodoGestion, CalendarioFuncionario
from .goal_models import AsignacionMeta

class ActivityVerificationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile
        from django.test import override_settings
        cls.media = tempfile.TemporaryDirectory(prefix='sgr-verif-tests-')
        cls.settings_override = override_settings(MEDIA_ROOT=cls.media.name)
        cls.settings_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.settings_override.disable()
        cls.media.cleanup()

    def setUp(self):
        self.d = Delegacion.objects.create(codigo='V-DEL', nombre='Delegación Verificación')
        self.role_supervisor = Rol.objects.create(
            nombre='Supervisor Revisor',
            permisos=['actividades.ver', 'actividades.ver_equipo', 'actividades.crear', 'actividades.editar', 'actividades.revisar', 'evidencias.ver', 'evidencias.crear', 'evidencias.revisar']
        )
        self.role_funcionario = Rol.objects.create(
            nombre='Funcionario Verif',
            permisos=['actividades.ver', 'actividades.crear', 'actividades.editar', 'evidencias.ver', 'evidencias.crear']
        )
        self.funcionario = Usuario.objects.create_user(
            'func_verif', email='func@test.local', password='PassFunc!123',
            delegacion=self.d, rol=self.role_funcionario
        )
        self.supervisor = Usuario.objects.create_user(
            'super_user', email='super@test.local', password='PassSuper!123',
            delegacion=self.d, rol=self.role_supervisor
        )
        self.p = PeriodoGestion.objects.create(
            codigo='T126V', nombre='Trimestre 1 2026 Verif', anio=2026, numero=1,
            fecha_inicio='2026-01-01', fecha_fin='2026-03-31'
        )
        self.item = ItemMeta.objects.create(
            codigo='ITEM-V', nombre='Atención vecinal con respaldo',
            tipo='Actividad', requiere_evidencia=True
        )
        self.item_sin_evidencia = ItemMeta.objects.create(
            codigo='ITEM-NOEV', nombre='Gestión directa sin archivo',
            tipo='Actividad', requiere_evidencia=False
        )

    def create_activity(self, author=None, item=None, **extra):
        u = author or self.funcionario
        i = item or self.item
        values = dict(
            autor=u, delegacion=self.d, item=i,
            fecha=date(2026, 1, 15),
            solicitud='Solicitud vecinal inicial',
            accion='Atención en terreno realizada',
            sector='Norte',
            estado='Pendiente',
            elegibilidad_snapshot={'potencialmente_puntuable': True, 'motivos': [], 'clasificacion': 'Ejecución', 'estado': 'Potencialmente puntuable'}
        ) | extra
        return Actividad.objects.create(**values)

    def test_author_cannot_review_own_activity(self):
        # El supervisor tiene permiso de revisar, pero como autor de esta actividad no puede revisarse a sí mismo
        a = self.create_activity(author=self.supervisor)
        self.client.force_login(self.supervisor)
        r = self.client.post(
            f'/api/operacion/actividades/{a.pk}/revisar/',
            {'_version': a.version, 'decision': 'Aprobada y pondera', 'observacion': 'Intento auto-aprobación'},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn('autor no puede revisar', str(r.json()['error']))

    def test_explicit_decisions_and_revision_actividad_model(self):
        a = self.create_activity()
        self.client.force_login(self.supervisor)
        
        # 1. Solicitud de antecedentes
        r = self.client.post(
            f'/api/operacion/actividades/{a.pk}/revisar/',
            {'_version': a.version, 'decision': 'Solicitud de antecedentes', 'observacion': 'Falta documento de respaldo'},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 200, r.content)
        a.refresh_from_db()
        self.assertEqual(a.estado, 'Solicitud de antecedentes')
        rev = a.revisiones.first()
        self.assertIsNotNone(rev)
        self.assertEqual(rev.decision, 'Solicitud de antecedentes')
        self.assertFalse(rev.pondera)
        self.assertEqual(rev.observacion, 'Falta documento de respaldo')
        self.assertEqual(rev.autor, self.supervisor)

        # 2. Aprobada y no pondera
        r = self.client.post(
            f'/api/operacion/actividades/{a.pk}/revisar/',
            {'_version': a.version, 'decision': 'Aprobada y no pondera', 'observacion': 'Registro informativo válido pero no suma meta'},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 200, r.content)
        a.refresh_from_db()
        self.assertEqual(a.estado, 'Aprobada y no pondera')
        rev2 = a.revisiones.first()
        self.assertEqual(rev2.decision, 'Aprobada y no pondera')
        self.assertFalse(rev2.pondera)

        # 3. Aprobada y pondera
        r = self.client.post(
            f'/api/operacion/actividades/{a.pk}/revisar/',
            {'_version': a.version, 'decision': 'Aprobada y pondera', 'observacion': 'Cumple íntegramente las condiciones'},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 200, r.content)
        a.refresh_from_db()
        self.assertEqual(a.estado, 'Aprobada y pondera')
        rev3 = a.revisiones.first()
        self.assertEqual(rev3.decision, 'Aprobada y pondera')
        self.assertTrue(rev3.pondera)
        self.assertEqual(a.revisiones.count(), 3)

    def test_version_concurrency_and_empty_observation(self):
        a = self.create_activity()
        self.client.force_login(self.supervisor)
        # Observación vacía rechazada
        r = self.client.post(
            f'/api/operacion/actividades/{a.pk}/revisar/',
            {'_version': a.version, 'decision': 'Aprobada y pondera', 'observacion': '   '},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 400)

        # Versión errónea rechazada con 409
        r = self.client.post(
            f'/api/operacion/actividades/{a.pk}/revisar/',
            {'_version': 999, 'decision': 'Aprobada y pondera', 'observacion': 'Observación'},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 409)

    def test_author_can_edit_pending_and_antecedentes_requeues_to_pending(self):
        a = self.create_activity(estado='Solicitud de antecedentes')
        self.client.force_login(self.funcionario)
        
        # Edición por el autor
        r = self.client.patch(
            f'/api/operacion/actividades/{a.pk}/',
            {'_version': a.version, 'accion': 'Atención corregida y antecedentes añadidos'},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 200, r.content)
        a.refresh_from_db()
        self.assertEqual(a.accion, 'Atención corregida y antecedentes añadidos')
        # Re-cola automáticamente a Pendiente
        self.assertEqual(a.estado, 'Pendiente')

    def test_approved_and_annulled_activities_are_strictly_locked(self):
        for state in ['Aprobada y pondera', 'Aprobada y no pondera', 'Anulada']:
            a = self.create_activity(estado=state)
            self.client.force_login(self.funcionario)
            # Intento de edición bloqueado
            r = self.client.patch(
                f'/api/operacion/actividades/{a.pk}/',
                {'_version': a.version, 'accion': 'Modificación no permitida'},
                content_type='application/json'
            )
            self.assertEqual(r.status_code, 400)
            self.assertIn('bloqueadas', str(r.json()['error']))

            # Intento de subir evidencia bloqueado
            pdf = SimpleUploadedFile('test.pdf', b'%PDF-1.4\n%%EOF', content_type='application/pdf')
            r2 = self.client.post(
                '/api/operacion/evidencias/',
                {'actividad': a.pk, 'descripcion': 'Evidencia tardía', 'archivo': pdf}
            )
            self.assertEqual(r2.status_code, 400)

    def test_annul_activity_with_justification(self):
        a = self.create_activity()
        self.client.force_login(self.supervisor)
        # Sin motivo falla
        r = self.client.post(
            f'/api/operacion/actividades/{a.pk}/anular/',
            {'_version': a.version, 'motivo': ''},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 400)

        # Con motivo anula y audita
        r = self.client.post(
            f'/api/operacion/actividades/{a.pk}/anular/',
            {'_version': a.version, 'motivo': 'Registro duplicado por error operativo'},
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 200, r.content)
        a.refresh_from_db()
        self.assertEqual(a.estado, 'Anulada')
        rev = a.revisiones.first()
        self.assertEqual(rev.decision, 'Anulada')
        self.assertFalse(rev.pondera)
        self.assertEqual(rev.observacion, 'Registro duplicado por error operativo')
        self.assertTrue(EventoLocal.objects.filter(recurso='actividades', accion='anular').exists())

    def test_performance_calculation_120_percent_and_pondering_states(self):
        from .performance import enrich

        # Calendario funcionario disponible
        cal = CalendarioFuncionario.objects.create(
            autor=self.supervisor, delegacion=self.d,
            funcionario=self.funcionario, periodo=self.p,
            semana={'lunes': 'Completa', 'martes': 'Completa', 'miercoles': 'Completa', 'jueves': 'Completa', 'viernes': 'Completa'},
            motivo='Jornada regular'
        )
        # Asignación individual: Objetivo 80, Peso 20%
        assignment = AsignacionMeta.objects.create(
            funcionario=self.funcionario, item=self.item_sin_evidencia,
            periodo=self.p, delegacion=self.d, cantidad_objetivo=80,
            ponderacion=20, autor=self.supervisor
        )

        # Registrar 100 actividades aprobadas que ponderan
        # Objetivo 80 -> 100 aprobadas que ponderan producen 125% bruto, 120% tope, 24 puntos ponderados
        actividades_ponderan = [
            Actividad(
                autor=self.funcionario, delegacion=self.d, item=self.item_sin_evidencia,
                asignacion_meta=assignment, fecha=date(2026, 1, 10),
                solicitud=f'Caso {i}', accion='Ejecutado', sector='Norte',
                estado='Aprobada y pondera',
                elegibilidad_snapshot={'potencialmente_puntuable': True, 'motivos': [], 'clasificacion': 'Ejecución', 'estado': 'Potencialmente puntuable'}
            )
            for i in range(100)
        ]
        Actividad.objects.bulk_create(actividades_ponderan)

        # Registrar 10 actividades "Aprobada y no pondera" -> aportan 0
        actividades_no_ponderan = [
            Actividad(
                autor=self.funcionario, delegacion=self.d, item=self.item_sin_evidencia,
                asignacion_meta=assignment, fecha=date(2026, 1, 15),
                solicitud=f'Caso no pondera {i}', accion='Ejecutado informativo', sector='Norte',
                estado='Aprobada y no pondera',
                elegibilidad_snapshot={'potencialmente_puntuable': True, 'motivos': [], 'clasificacion': 'Ejecución', 'estado': 'Potencialmente puntuable'}
            )
            for i in range(10)
        ]
        Actividad.objects.bulk_create(actividades_no_ponderan)

        base_res = {
            'funcionario': self.funcionario.pk,
            'delegacion': self.d.pk,
            'dias_disponibles': 60,
            'dias_disponibles_transcurridos': 60,
            'metas': [{
                'item': self.item_sin_evidencia.pk,
                'asignacion_meta': assignment.pk,
                'meta_original': '80.00',
                'meta_ajustada_exacta': '80.00',
                'meta_ajustada': '80.00',
                'ponderacion': '20.00',
                'prorrateable': False,
            }]
        }
        res = enrich(base_res, cal, self.p, self.funcionario)
        meta_res = res['metas'][0]
        # Cumplimiento limitado a 120.00 %
        self.assertEqual(meta_res['cumplimiento'], '120.00')
        # Aporte ponderado = 120% * 20% = 24.00 puntos
        self.assertEqual(meta_res['aporte_ponderado'], '24.00')
        # Total registrado: 110 (100 ponderan + 10 no ponderan)
        self.assertEqual(meta_res['total_registrado'], 110)
        # Validas para ponderar: 100
        self.assertEqual(meta_res['validas'], 100)
        # Unidades reconocidas con tope 120% de 80 = 96.00
        self.assertEqual(meta_res['unidades_reconocidas'], '96.00')
