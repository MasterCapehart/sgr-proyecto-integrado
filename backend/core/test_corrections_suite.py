from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.utils import timezone
from core.models import Delegacion, Rol, Usuario, ItemMeta, PeriodoGestion, Actividad, Evidencia, Atencion, RecuperacionAcceso, ConfiguracionMeta
from core.goal_models import AsignacionMeta
from core.domain_models import RevisionActividad, RevisionEvidencia
from core import collective, excel_api

class CorrectionsSuiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.d1 = Delegacion.objects.create(codigo='DEL01', nombre='Delegación Centro')
        self.d2 = Delegacion.objects.create(codigo='DEL02', nombre='Delegación Norte')

        self.r_admin, _ = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={'alcance': 'global', 'permisos': [
                'actividades.revisar', 'actividades.crear', 'actividades.ver', 'actividades.editar', 'actividades.editar_equipo',
                'evidencias.revisar', 'evidencias.crear', 'evidencias.ver',
                'usuarios.crear', 'usuarios.ver', 'usuarios.editar', 'atenciones.crear', 'atenciones.ver',
                'asignaciones-metas.crear', 'asignaciones-metas.ver', 'asignaciones-metas.editar'
            ]}
        )
        # Aseguramos los permisos necesarios si ya existía el rol
        for p in ['actividades.revisar', 'actividades.crear', 'actividades.ver', 'actividades.editar', 'actividades.editar_equipo',
                  'evidencias.revisar', 'evidencias.crear', 'evidencias.ver',
                  'usuarios.crear', 'usuarios.ver', 'usuarios.editar', 'atenciones.crear', 'atenciones.ver',
                  'asignaciones-metas.crear', 'asignaciones-metas.ver', 'asignaciones-metas.editar']:
            if p not in self.r_admin.permisos:
                self.r_admin.permisos.append(p)
        self.r_admin.save()

        self.r_verif = Rol.objects.create(
            nombre='Verificador_QA_Suite', alcance='delegacion',
            permisos=['actividades.revisar', 'actividades.ver', 'actividades.anular', 'evidencias.revisar', 'evidencias.ver']
        )
        self.r_func = Rol.objects.create(
            nombre='Funcionario_QA_Suite', alcance='delegacion',
            permisos=['actividades.crear', 'actividades.ver', 'actividades.editar', 'evidencias.crear', 'evidencias.ver', 'atenciones.crear', 'atenciones.ver']
        )

        self.admin = Usuario.objects.create_superuser('admin.qa', email='admin@qa.test', password='Password123!', rol=self.r_admin, delegacion=self.d1)
        self.admin.delegaciones.set([self.d1, self.d2])

        self.revisor_d1 = Usuario.objects.create_user('revisor.d1', email='revisor1@qa.test', password='Password123!', rol=self.r_verif, delegacion=self.d1)
        self.revisor_d1.delegaciones.set([self.d1])

        self.revisor_d2 = Usuario.objects.create_user('revisor.d2', email='revisor2@qa.test', password='Password123!', rol=self.r_verif, delegacion=self.d2)
        self.revisor_d2.delegaciones.set([self.d2])

        self.func_d1 = Usuario.objects.create_user('func.d1', email='func1@qa.test', password='Password123!', rol=self.r_func, delegacion=self.d1)
        self.func_d1.delegaciones.set([self.d1])

        self.item = ItemMeta.objects.create(codigo='ITM01', nombre='Atención en terreno', tipo='Operativo', requiere_evidencia=True)
        self.item2 = ItemMeta.objects.create(codigo='ITM02', nombre='Operativo Social', tipo='Operativo', requiere_evidencia=False)
        self.periodo = PeriodoGestion.objects.create(codigo='PER-2026-Q1', nombre='2026-Q1', anio=2026, numero=1, fecha_inicio=date(2026, 1, 1), fecha_fin=date(2026, 3, 31), cerrado=False)

    # 1. Permisos de revisión: impedir que revisor apruebe o anule actividades de otra delegación
    def test_revisor_no_puede_revisar_actividad_otra_delegacion(self):
        act = Actividad.objects.create(
            autor=self.func_d1, delegacion=self.d1, item=self.item, fecha=date(2026, 2, 10),
            solicitud='Atención comunitaria', accion='Visita', contacto='Vecino', telefono='912345678',
            estado='Pendiente', elegibilidad_snapshot={'potencialmente_puntuable': True, 'motivos': [], 'clasificacion': 'Ejecución', 'estado': 'Potencialmente puntuable'}
        )
        self.client.force_login(self.revisor_d2)
        res = self.client.post(
            f'/api/operacion/actividades/{act.pk}/revisar/',
            {'_version': act.version, 'decision': 'Aprobada y pondera', 'observacion': 'Aprobado'},
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn('otra delegación', res.json()['error']['message'])

    def test_revisor_no_puede_anular_actividad_otra_delegacion(self):
        act = Actividad.objects.create(
            autor=self.func_d1, delegacion=self.d1, item=self.item, fecha=date(2026, 2, 10),
            solicitud='Atención comunitaria', accion='Visita', contacto='Vecino', telefono='912345678',
            estado='Pendiente', elegibilidad_snapshot={'potencialmente_puntuable': True, 'motivos': [], 'clasificacion': 'Ejecución', 'estado': 'Potencialmente puntuable'}
        )
        self.client.force_login(self.revisor_d2)
        res = self.client.post(
            f'/api/operacion/actividades/{act.pk}/anular/',
            {'_version': act.version, 'motivo': 'Anulada por error'},
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn('otra delegación', res.json()['error']['message'])

    # 2. Trimestres cerrados: bloquear revisiones y anulaciones mientras esté cerrado
    def test_trimestre_cerrado_bloquea_revision_y_anulacion(self):
        self.periodo.cerrado = True
        self.periodo.save()
        act = Actividad.objects.create(
            autor=self.func_d1, delegacion=self.d1, item=self.item, fecha=date(2026, 2, 10),
            solicitud='Atención comunitaria', accion='Visita', contacto='Vecino', telefono='912345678',
            estado='Pendiente', elegibilidad_snapshot={'potencialmente_puntuable': True, 'motivos': [], 'clasificacion': 'Ejecución', 'estado': 'Potencialmente puntuable'}
        )
        self.client.force_login(self.revisor_d1)
        res_rev = self.client.post(
            f'/api/operacion/actividades/{act.pk}/revisar/',
            {'_version': act.version, 'decision': 'Aprobada y pondera', 'observacion': 'Aprobado'},
            content_type='application/json'
        )
        self.assertEqual(res_rev.status_code, 400)
        self.assertIn('cerrado', res_rev.json()['error']['message'])

        res_anul = self.client.post(
            f'/api/operacion/actividades/{act.pk}/anular/',
            {'_version': act.version, 'motivo': 'Anular'},
            content_type='application/json'
        )
        self.assertEqual(res_anul.status_code, 400)
        self.assertIn('cerrado', res_anul.json()['error']['message'])

    # 3. Decisión de ponderación: aprobar evidencia no aprueba actividad automáticamente
    def test_aprobar_archivos_no_aprueba_actividad_para_ponderar(self):
        act = Actividad.objects.create(
            autor=self.func_d1, delegacion=self.d1, item=self.item, fecha=date(2026, 2, 10),
            solicitud='Atención comunitaria', accion='Visita', contacto='Vecino', telefono='912345678',
            estado='Pendiente', elegibilidad_snapshot={'potencialmente_puntuable': True, 'motivos': [], 'clasificacion': 'Ejecución', 'estado': 'Potencialmente puntuable'}
        )
        evi = Evidencia.objects.create(
            actividad=act, autor=self.func_d1, delegacion=self.d1, archivo='doc.pdf', nombre_archivo='doc.pdf',
            tipo_mime='application/pdf', tamano=100, sha256='c'*64, descripcion='Respaldo', estado='Pendiente', version=1
        )
        self.client.force_login(self.revisor_d1)
        res_evi = self.client.post(
            f'/api/operacion/evidencias/{evi.pk}/revisar/',
            {'_version': evi.version, 'decision': 'Aprobada', 'observacion': 'Archivo correcto'},
            content_type='application/json'
        )
        self.assertEqual(res_evi.status_code, 200)

        act.refresh_from_db()
        self.assertEqual(act.estado, 'Validada')

        evi.refresh_from_db()
        self.assertEqual(evi.estado, 'Aprobada')

        from core.performance import reasons
        motivos = reasons(act, [evi])
        self.assertIn('Evidencia aprobada; la actividad requiere decisión vigente de "Aprobada y pondera" para sumar a la meta.', motivos)

        res_act = self.client.post(
            f'/api/operacion/actividades/{act.pk}/revisar/',
            {'_version': act.version, 'decision': 'Aprobada y pondera', 'observacion': 'Verificada integralmente'},
            content_type='application/json'
        )
        self.assertEqual(res_act.status_code, 200)
        act.refresh_from_db()
        self.assertEqual(act.estado, 'Aprobada y pondera')
        motivos_post = reasons(act, [evi])
        self.assertEqual(motivos_post, [])

    # 4. Activación de usuarios por correo sin contraseña obligatoria
    def test_activacion_usuario_sin_password_admin(self):
        self.client.force_login(self.admin)
        payload = {
            'username': 'nuevo.funcionario',
            'first_name': 'Nuevo',
            'last_name': 'Funcionario',
            'email': 'nuevo.func@qa.test',
            'rol': self.r_func.pk,
            'delegacion': self.d1.pk,
            'delegaciones': [self.d1.pk],
            'estado': True,
            'activar_por_correo': True
        }
        res = self.client.post('/api/usuarios/', payload, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        created_user = Usuario.objects.get(username='nuevo.funcionario')
        self.assertFalse(created_user.has_usable_password())
        self.assertTrue(RecuperacionAcceso.objects.filter(usuario=created_user).exists())

    # 5. Dashboard trimestral: filtros y links a registros
    def test_dashboard_trimestral_urls_y_filtros(self):
        self.client.force_login(self.func_d1)
        res = self.client.get('/api/mi-progreso/?trimestre=2026-Q1')
        self.assertEqual(res.status_code, 200)
        data = res.json()['data']
        self.assertIn('attentions_url', data['month'])
        self.assertIn('activities_url', data['month'])
        self.assertIn('commitments_url', data['month'])
        self.assertIn('evidence_url', data['month'])
        self.assertIn('delegation', data)

    # 6. Planes individuales: validación de 100% de ponderación antes de aprobar
    def test_plan_individual_exige_100_por_ciento(self):
        self.client.force_login(self.admin)
        # Intentar aprobar plan sumando 40% (debe fallar)
        payload_invalido = {
            'funcionario': self.func_d1.pk,
            'item': self.item.pk,
            'periodo': self.periodo.pk,
            'cantidad_objetivo': '10',
            'ponderacion': '40.00',
            'estado': True,
            'aprobar_plan': True
        }
        res_inv = self.client.post('/api/asignaciones-metas/', payload_invalido, content_type='application/json')
        self.assertEqual(res_inv.status_code, 400)
        self.assertIn('100 %', res_inv.json()['error']['message'])

        # Como propuesta (sin aprobar), sí se permite guardar mientras se elabora
        payload_propuesta = {
            'funcionario': self.func_d1.pk,
            'item': self.item.pk,
            'periodo': self.periodo.pk,
            'cantidad_objetivo': '10',
            'ponderacion': '40.00',
            'estado': True,
            'es_propuesta': True
        }
        res_prop = self.client.post('/api/asignaciones-metas/', payload_propuesta, content_type='application/json')
        self.assertEqual(res_prop.status_code, 201)
        asig = AsignacionMeta.objects.get(funcionario=self.func_d1, item=self.item)
        self.assertTrue(asig.snapshot.get('es_propuesta'))
        self.assertFalse(asig.snapshot.get('plan_aprobado'))

        # Completar al 100% y aprobar plan
        payload_completar = {
            'funcionario': self.func_d1.pk,
            'item': self.item2.pk,
            'periodo': self.periodo.pk,
            'cantidad_objetivo': '15',
            'ponderacion': '60.00',
            'estado': True,
            'aprobar_plan': True
        }
        res_comp = self.client.post('/api/asignaciones-metas/', payload_completar, content_type='application/json')
        self.assertEqual(res_comp.status_code, 201)

    # 7. Cálculo colectivo: consolidar personas con distintas ponderaciones
    def test_calculo_colectivo_ponderaciones_distintas(self):
        u1_summary = {
            'funcionario': 1, 'funcionario_nombre': 'User 1', 'area': 'Operaciones', 'objetivo_al_dia': '100',
            'metas': [{'item': 10, 'codigo': 'IT10', 'nombre': 'Atenciones', 'meta_ajustada_exacta': '10', 'unidades_reconocidas_exactas': '8', 'ponderacion': '25.00', 'cumplimiento_exacto': '80.00', 'validas': 8, 'total_registrado': 8}]
        }
        u2_summary = {
            'funcionario': 2, 'funcionario_nombre': 'User 2', 'area': 'Operaciones', 'objetivo_al_dia': '100',
            'metas': [{'item': 10, 'codigo': 'IT10', 'nombre': 'Atenciones', 'meta_ajustada_exacta': '10', 'unidades_reconocidas_exactas': '9', 'ponderacion': '35.00', 'cumplimiento_exacto': '90.00', 'validas': 9, 'total_registrado': 9}]
        }
        res = collective.consolidate([u1_summary, u2_summary])
        self.assertFalse(res['pesos_compatibles'])
        self.assertIsNone(res['cumplimiento'])
        self.assertEqual(res['items'][0]['cumplimiento'], '85.00')

    # 8. Tiempos de gestión social: fechas correctas, sin negativos, faltantes no calculables
    def test_tiempos_gestion_social_no_negativos_e_incompletos(self):
        d1 = date(2026, 2, 1)
        d2 = date(2026, 2, 5)
        self.assertEqual(excel_api.diff_days(d1, d2), 4)
        self.assertIsNone(excel_api.diff_days(d2, d1))
        self.assertIsNone(excel_api.diff_days(d1, None))
        self.assertIsNone(excel_api.diff_days(None, d2))
