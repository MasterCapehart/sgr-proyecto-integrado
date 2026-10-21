import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import Usuario, Delegacion, Rol, ItemMeta, Cargo, Actividad, Compromiso, Evidencia

class RolePermissionsWorkflowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media = tempfile.TemporaryDirectory(prefix='sgr-role-tests-')
        cls.settings_override = override_settings(MEDIA_ROOT=cls.media.name)
        cls.settings_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.settings_override.disable()
        cls.media.cleanup()

    def setUp(self):
        self.delegacion = Delegacion.objects.create(codigo='DEL-01', nombre='Delegación Centro')
        self.otra_delegacion = Delegacion.objects.create(codigo='DEL-02', nombre='Delegación Norte')

        self.cargo_territorial = Cargo.objects.create(
            codigo='TERR', nombre='Territorial OO.CC.', area='Territorial', planilla='TERRITORIAL'
        )
        self.item_meta = ItemMeta.objects.create(
            codigo='IT-01', nombre='Reunión comunitaria', unidad_medida='Reunión'
        )
        self.item_meta.cargos.add(self.cargo_territorial)

        # 1. Rol Funcionario: registrar trabajo, consultar pendientes, sin administración
        self.rol_funcionario = Rol.objects.create(
            nombre='Funcionario',
            permisos=[
                'actividades.ver', 'actividades.crear', 'actividades.editar',
                'compromisos.ver', 'compromisos.crear',
                'evidencias.ver', 'evidencias.crear',
                'atenciones.ver', 'atenciones.crear',
                'conversaciones.crear',
            ]
        )
        self.user_funcionario = Usuario.objects.create_user(
            username='funcionario_test',
            email='funcionario@laserena.test',
            password='Password123!',
            rol=self.rol_funcionario,
            delegacion=self.delegacion,
            cargo=self.cargo_territorial
        )
        self.user_funcionario.delegaciones.add(self.delegacion)

        # 2. Rol Verificador: revisar evidencias ajenas, solicitar correcciones, sin administración
        self.rol_verificador = Rol.objects.create(
            nombre='Verificador',
            permisos=[
                'actividades.ver', 'actividades.ver_equipo',
                'evidencias.ver', 'evidencias.revisar',
                'conversaciones.crear',
            ]
        )
        self.user_verificador = Usuario.objects.create_user(
            username='verificador_test',
            email='verificador@laserena.test',
            password='Password123!',
            rol=self.rol_verificador,
            delegacion=self.delegacion
        )
        self.user_verificador.delegaciones.add(self.delegacion)

        # 3. Rol Delegado / Coordinador: consultar y dar seguimiento al equipo
        self.rol_coordinador = Rol.objects.create(
            nombre='Coordinador',
            permisos=[
                'actividades.ver', 'actividades.ver_equipo',
                'compromisos.ver', 'compromisos.ver_equipo', 'compromisos.editar', 'compromisos.editar_equipo',
                'evidencias.ver', 'evidencias.ver_equipo',
                'reportes.ver', 'conversaciones.crear',
            ]
        )
        self.user_coordinador = Usuario.objects.create_user(
            username='coordinador_test',
            email='coordinador@laserena.test',
            password='Password123!',
            rol=self.rol_coordinador,
            delegacion=self.delegacion
        )
        self.user_coordinador.delegaciones.add(self.delegacion)

        # 4. Rol Consulta: solo lectura, sin crear ni modificar
        self.rol_consulta = Rol.objects.create(
            nombre='Consulta',
            permisos=[
                'actividades.ver', 'actividades.ver_equipo',
                'compromisos.ver', 'compromisos.ver_equipo',
                'evidencias.ver', 'evidencias.ver_equipo',
                'reportes.ver',
            ]
        )
        self.user_consulta = Usuario.objects.create_user(
            username='consulta_test',
            email='consulta@laserena.test',
            password='Password123!',
            rol=self.rol_consulta,
            delegacion=self.delegacion
        )
        self.user_consulta.delegaciones.add(self.delegacion)

    def test_funcionario_no_puede_acceder_a_opciones_administrativas(self):
        """El funcionario no tiene acceso a endpoints de administración."""
        self.client.force_login(self.user_funcionario)
        rutas_prohibidas = [
            '/api/roles/',
            '/api/usuarios/',
            '/api/delegaciones/',
            '/api/periodos/',
            '/api/auditoria/',
            '/api/gobierno/',
            '/api/items-metas/',
            '/api/configuraciones-metas/',
        ]
        for ruta in rutas_prohibidas:
            with self.subTest(ruta=ruta):
                res = self.client.get(ruta)
                self.assertEqual(res.status_code, 403, f'Acceso no bloqueado a {ruta}')

        # Tampoco puede revisar evidencias en bandeja de validación
        res_revisar = self.client.post('/api/operacion/evidencias/1/revisar/', {'decision': 'Aprobada'}, content_type='application/json')
        self.assertEqual(res_revisar.status_code, 403)

    def test_verificador_no_puede_acceder_a_administracion(self):
        """El verificador no tiene acceso a endpoints de administración ni a crear actividades."""
        self.client.force_login(self.user_verificador)
        rutas_prohibidas = [
            '/api/roles/',
            '/api/usuarios/',
            '/api/delegaciones/',
            '/api/periodos/',
            '/api/auditoria/',
        ]
        for ruta in rutas_prohibidas:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).status_code, 403)

        # Tampoco puede registrar actividades
        res_actividad = self.client.post('/api/operacion/actividades/', {}, content_type='application/json')
        self.assertEqual(res_actividad.status_code, 403)

    def test_consulta_no_puede_crear_ni_modificar(self):
        """El rol Consulta solo visualiza; cualquier creación o modificación es rechazada."""
        self.client.force_login(self.user_consulta)

        # Puede visualizar actividades y compromisos
        self.assertEqual(self.client.get('/api/operacion/actividades/').status_code, 200)
        self.assertEqual(self.client.get('/api/operacion/compromisos/').status_code, 200)
        self.assertEqual(self.client.get('/api/operacion/evidencias/').status_code, 200)

        # Intentar crear actividad -> 403
        r_act = self.client.post('/api/operacion/actividades/', {'solicitud': 'Test'}, content_type='application/json')
        self.assertEqual(r_act.status_code, 403)

        # Intentar captura unificada -> 403
        r_cap = self.client.post('/api/captura/', {'clave_idempotencia': 'key-test'}, content_type='application/json')
        self.assertEqual(r_cap.status_code, 403)

        # Intentar crear compromiso -> 403
        r_comp = self.client.post('/api/operacion/compromisos/', {'descripcion': 'Test'}, content_type='application/json')
        self.assertEqual(r_comp.status_code, 403)

        # Intentar subir evidencia -> 403
        r_ev = self.client.post('/api/operacion/evidencias/', {'actividad': 1})
        self.assertEqual(r_ev.status_code, 403)

        # Intentar revisar evidencia -> 403
        r_rev = self.client.post('/api/operacion/evidencias/1/revisar/', {'decision': 'Aprobada'}, content_type='application/json')
        self.assertEqual(r_rev.status_code, 403)

    def test_coordinador_puede_dar_seguimiento_al_equipo(self):
        """El coordinador visualiza registros de otros miembros del equipo y puede dar seguimiento a compromisos."""
        # Creamos una actividad y compromiso a nombre del funcionario
        actividad = Actividad.objects.create(
            autor=self.user_funcionario,
            delegacion=self.delegacion,
            fecha=timezone.localdate(),
            solicitud='Solicitud funcionario',
            accion='Atención realizada',
            contacto='Vecino Juan',
            sector='Centro',
            item=self.item_meta,
            cargo=self.cargo_territorial,
            unidad=1
        )
        compromiso = Compromiso.objects.create(
            autor=self.user_funcionario,
            delegacion=self.delegacion,
            responsable=self.user_funcionario,
            descripcion='Compromiso del funcionario',
            solicitante='Vecino Juan',
            sector='Centro',
            fecha_comprometida=timezone.localdate(),
            origen='Interno',
            unidad=1
        )

        # Logueamos al coordinador
        self.client.force_login(self.user_coordinador)

        # 1. El coordinador ve la actividad del funcionario gracias a actividades.ver_equipo
        r_act = self.client.get('/api/operacion/actividades/')
        self.assertEqual(r_act.status_code, 200)
        ids_act = [x['id'] for x in r_act.json()['results']]
        self.assertIn(actividad.pk, ids_act)

        # 2. El coordinador ve el compromiso del funcionario gracias a compromisos.ver_equipo
        r_comp = self.client.get('/api/operacion/compromisos/')
        self.assertEqual(r_comp.status_code, 200)
        ids_comp = [x['id'] for x in r_comp.json()['results']]
        self.assertIn(compromiso.pk, ids_comp)

        # 3. El coordinador puede dar seguimiento / editar el compromiso gracias a compromisos.editar_equipo
        r_patch = self.client.patch(
            f'/api/operacion/compromisos/{compromiso.pk}/',
            {
                '_version': compromiso.version,
                'observacion': 'Seguimiento por coordinación: coordinado con cuadrilla',
                'responsable': self.user_coordinador.pk,
            },
            content_type='application/json'
        )
        self.assertEqual(r_patch.status_code, 200, r_patch.content)
        compromiso.refresh_from_db()
        self.assertEqual(compromiso.responsable, self.user_coordinador)

    def test_recorrido_registro_tubo_evidencia_revision_correccion(self):
        """
        Prueba el flujo completo:
        1. Registro: Funcionario crea actividad y seguimiento hacia el tubo.
        2. Tubo: Se valida existencia del compromiso generado en el tubo.
        3. Evidencia: Funcionario adjunta archivo de evidencia a su actividad.
        4. Verificador no puede auto-aprobar si fuera el autor; pero un verificador ajeno revisa.
        5. Revisión: Verificador ajeno solicita Corrección indicando observación obligatoria.
        6. Corrección: Funcionario consulta sus pendientes (mi-progreso) y subsana con reemplazo.
        7. Aprobación: Verificador aprueba la nueva versión y la actividad queda Validada.
        """
        # ==========================================
        # PASO 1: Registro (Captura unificada + Tubo)
        # ==========================================
        self.client.force_login(self.user_funcionario)
        payload_captura = {
            'clave_idempotencia': 'captura-flujo-001',
            'actividad': {
                'fecha': str(timezone.localdate()),
                'solicitud': 'Vecinos solicitan reparación de alumbrado',
                'accion': 'Recepción y coordinación de visita técnica',
                'contacto': 'María González',
                'telefono': '+56987654321',
                'sector': 'Villa San José',
                'item': self.item_meta.pk
            },
            'nuevo_compromiso': {
                'descripcion': 'Reparación de luminarias pasaje Los Aromos',
                'fecha_comprometida': str(timezone.localdate()),
                'sector': 'Villa San José',
                'responsable': self.user_funcionario.pk,
                'origen': 'Externo'
            }
        }
        res_reg = self.client.post('/api/captura/', payload_captura, content_type='application/json')
        self.assertEqual(res_reg.status_code, 201, res_reg.content)
        data_actividad = res_reg.json()['data']
        actividad_id = data_actividad['id']
        codigo_actividad = data_actividad['codigo']
        compromiso_id = data_actividad['compromiso']
        self.assertIsNotNone(compromiso_id, 'El compromiso debió ser creado en el tubo')

        # ==========================================
        # PASO 2: Tubo de trabajo
        # ==========================================
        res_tubo = self.client.get(f'/api/operacion/compromisos/{compromiso_id}/')
        self.assertEqual(res_tubo.status_code, 200)
        self.assertEqual(res_tubo.json()['data']['codigo_verificacion_foto'], codigo_actividad)

        # ==========================================
        # PASO 3: Evidencia
        # ==========================================
        archivo_evidencia = SimpleUploadedFile(
            'acta_reunion.pdf',
            b'%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>%%EOF',
            content_type='application/pdf'
        )
        res_ev = self.client.post(
            '/api/operacion/evidencias/',
            {
                'actividad': actividad_id,
                'descripcion': 'Acta de visita inicial firmada',
                'archivo': archivo_evidencia
            }
        )
        self.assertEqual(res_ev.status_code, 201, res_ev.content)
        data_evidencia = res_ev.json()['data']
        evidencia_id = data_evidencia['id']
        evidencia_version = data_evidencia['version']

        # La actividad ahora debe estar en Pendiente
        act = Actividad.objects.get(pk=actividad_id)
        self.assertEqual(act.estado, 'Pendiente')

        # Si el funcionario intenta revisar su propia evidencia -> 403 (no tiene permiso)
        r_auto = self.client.post(
            f'/api/operacion/evidencias/{evidencia_id}/revisar/',
            {'_version': evidencia_version, 'decision': 'Aprobada', 'observacion': 'Autoaprobada'},
            content_type='application/json'
        )
        self.assertEqual(r_auto.status_code, 403)

        # ==========================================
        # PASO 4 y 5: Revisión por Verificador ajeno
        # ==========================================
        self.client.force_login(self.user_verificador)

        # Si el verificador intentara revisar una evidencia suya (supongamos que creara una),
        # el backend lo prohíbe con 400 'El autor no puede revisar su propia evidencia.'
        # Aquí la evidencia es ajena (del funcionario), por lo que sí puede revisarla.

        # Revisión: Verificador devuelve con Corrección
        res_rev = self.client.post(
            f'/api/operacion/evidencias/{evidencia_id}/revisar/',
            {
                '_version': evidencia_version,
                'decision': 'Corrección',
                'observacion': 'El PDF no incluye la firma del presidente de la junta de vecinos.'
            },
            content_type='application/json'
        )
        self.assertEqual(res_rev.status_code, 200, res_rev.content)
        ev_devuelta = Evidencia.objects.get(pk=evidencia_id)
        self.assertEqual(ev_devuelta.estado, 'Corrección')

        act.refresh_from_db()
        self.assertEqual(act.estado, 'Corrección')

        # ==========================================
        # PASO 6: Funcionario consulta pendientes y subsana corrección
        # ==========================================
        self.client.force_login(self.user_funcionario)

        # Consulta mi-progreso
        r_progreso = self.client.get('/api/mi-progreso/')
        self.assertEqual(r_progreso.status_code, 200)
        pending_data = r_progreso.json()['data']['pending']
        self.assertGreaterEqual(pending_data['correction'], 1, 'Debe aparecer en corrección en pendientes')

        # Subsanación: Funcionario adjunta archivo corregido con reemplaza
        archivo_corregido = SimpleUploadedFile(
            'acta_reunion_firmada.pdf',
            b'%PDF-1.4\n2 0 obj<<>>endobj\ntrailer<<>>%%EOF',
            content_type='application/pdf'
        )
        res_reemplazo = self.client.post(
            '/api/operacion/evidencias/',
            {
                'actividad': actividad_id,
                'reemplaza': evidencia_id,
                'descripcion': 'Acta con firma del presidente incorporada',
                'archivo': archivo_corregido
            }
        )
        self.assertEqual(res_reemplazo.status_code, 201, res_reemplazo.content)
        nueva_evidencia = res_reemplazo.json()['data']
        nueva_evidencia_id = nueva_evidencia['id']
        nueva_evidencia_ver = nueva_evidencia['version']

        # Verificar que la versión anterior quedó reemplazada y no vigente
        ev_anterior = Evidencia.objects.get(pk=evidencia_id)
        self.assertIsNotNone(ev_anterior.siguiente_version)

        # La actividad vuelve a quedar en Pendiente para validación
        act.refresh_from_db()
        self.assertEqual(act.estado, 'Pendiente')

        # ==========================================
        # PASO 7: Aprobación final por Verificador
        # ==========================================
        self.client.force_login(self.user_verificador)
        res_aprob = self.client.post(
            f'/api/operacion/evidencias/{nueva_evidencia_id}/revisar/',
            {
                '_version': nueva_evidencia_ver,
                'decision': 'Aprobada',
                'observacion': 'Acta conforme y firmas verificadas.'
            },
            content_type='application/json'
        )
        self.assertEqual(res_aprob.status_code, 200, res_aprob.content)

        act.refresh_from_db()
        self.assertEqual(act.estado, 'Validada')

        # ==========================================
        # PASO 8: Actividad validada queda protegida contra modificaciones
        # ==========================================
        self.client.force_login(self.user_funcionario)
        res_edit_bloqueada = self.client.patch(
            f'/api/operacion/actividades/{actividad_id}/',
            {'_version': act.version, 'accion': 'Intento de alterar registro validado'},
            content_type='application/json'
        )
        self.assertEqual(res_edit_bloqueada.status_code, 400)
        self.assertIn('Solo se editan actividades en borrador o devueltas', res_edit_bloqueada.json()['error']['message'])

        otro_archivo = SimpleUploadedFile('extra.pdf', b'%PDF-1.4\n%%EOF', content_type='application/pdf')
        res_adjuntar_bloqueado = self.client.post(
            '/api/operacion/evidencias/',
            {'actividad': actividad_id, 'descripcion': 'Intento adjuntar a validada', 'archivo': otro_archivo}
        )
        self.assertEqual(res_adjuntar_bloqueado.status_code, 400)
        self.assertIn('La actividad está validada', res_adjuntar_bloqueado.json()['error']['message'])

    def test_verificador_no_puede_revisar_evidencia_propia(self):
        """Si un verificador es autor de una actividad o evidencia, no puede auto-aprobarla."""
        # Le otorgamos temporalmente permisos de crear al verificador para que cree un registro propio
        self.rol_verificador.permisos += ['actividades.crear', 'actividades.editar', 'evidencias.crear']
        self.rol_verificador.save()

        self.client.force_login(self.user_verificador)
        actividad = Actividad.objects.create(
            autor=self.user_verificador,
            delegacion=self.delegacion,
            fecha=timezone.localdate(),
            solicitud='Actividad del propio verificador',
            accion='Atención propia',
            contacto='Vecino',
            sector='Centro',
            item=self.item_meta,
            unidad=1
        )
        archivo = SimpleUploadedFile('propia.pdf', b'%PDF-1.4\n%%EOF', content_type='application/pdf')
        res_ev = self.client.post(
            '/api/operacion/evidencias/',
            {'actividad': actividad.pk, 'descripcion': 'Evidencia propia', 'archivo': archivo}
        )
        self.assertEqual(res_ev.status_code, 201)
        ev_propia_id = res_ev.json()['data']['id']
        ev_propia_ver = res_ev.json()['data']['version']

        # El verificador intenta revisar su propia evidencia -> debe ser rechazado
        res_autorev = self.client.post(
            f'/api/operacion/evidencias/{ev_propia_id}/revisar/',
            {'_version': ev_propia_ver, 'decision': 'Aprobada', 'observacion': 'Me auto-apruebo'},
            content_type='application/json'
        )
        self.assertEqual(res_autorev.status_code, 400)
        self.assertIn('El autor no puede revisar su propia evidencia', res_autorev.json()['error']['message'])

    def test_observacion_obligatoria_en_revision(self):
        """La revisión exige obligatoriamente una observación no vacía."""
        actividad = Actividad.objects.create(
            autor=self.user_funcionario,
            delegacion=self.delegacion,
            fecha=timezone.localdate(),
            solicitud='Solicitud para revisión',
            accion='Atención',
            contacto='Vecino',
            sector='Centro',
            item=self.item_meta,
            unidad=1
        )
        self.client.force_login(self.user_funcionario)
        archivo = SimpleUploadedFile('doc.pdf', b'%PDF-1.4\n%%EOF', content_type='application/pdf')
        res_ev = self.client.post(
            '/api/operacion/evidencias/',
            {'actividad': actividad.pk, 'descripcion': 'Doc', 'archivo': archivo}
        )
        ev_id = res_ev.json()['data']['id']
        ev_ver = res_ev.json()['data']['version']

        self.client.force_login(self.user_verificador)
        # Intento sin observación
        res_sin_obs = self.client.post(
            f'/api/operacion/evidencias/{ev_id}/revisar/',
            {'_version': ev_ver, 'decision': 'Aprobada', 'observacion': '   '},
            content_type='application/json'
        )
        self.assertEqual(res_sin_obs.status_code, 400)
        self.assertIn('Indica una observación', res_sin_obs.json()['error']['message'])

    def test_contexto_devuelve_permisos_acordes_para_frontend(self):
        """Verifica que /api/contexto/ exponga exactamente los permisos autorizados para el renderizado del frontend."""
        # 1. Funcionario
        self.client.force_login(self.user_funcionario)
        c_func = self.client.get('/api/contexto/').json()['data']
        self.assertIn('actividades.crear', c_func['permisos'])
        self.assertNotIn('roles.ver', c_func['permisos'])
        self.assertNotIn('usuarios.ver', c_func['permisos'])
        self.assertNotIn('evidencias.revisar', c_func['permisos'])

        # 2. Verificador
        self.client.force_login(self.user_verificador)
        c_ver = self.client.get('/api/contexto/').json()['data']
        self.assertIn('evidencias.revisar', c_ver['permisos'])
        self.assertNotIn('actividades.crear', c_ver['permisos'])
        self.assertNotIn('usuarios.ver', c_ver['permisos'])

        # 3. Consulta
        self.client.force_login(self.user_consulta)
        c_con = self.client.get('/api/contexto/').json()['data']
        self.assertIn('actividades.ver', c_con['permisos'])
        self.assertNotIn('actividades.crear', c_con['permisos'])
        self.assertNotIn('compromisos.crear', c_con['permisos'])
        self.assertNotIn('evidencias.revisar', c_con['permisos'])
        self.assertNotIn('usuarios.ver', c_con['permisos'])
