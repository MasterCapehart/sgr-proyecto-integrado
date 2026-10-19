from datetime import datetime, time, timedelta
from django.test import TestCase
from django.utils import timezone
from .models import Delegacion, Rol, Usuario, ItemMeta, Actividad, Evidencia, Compromiso


class PersonalProgressTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()
        self.d = Delegacion.objects.create(codigo='PROG', nombre='Delegación progreso')
        self.foreign = Delegacion.objects.create(codigo='PROG2', nombre='Otra delegación')
        self.role = Rol.objects.create(nombre='Progreso personal', permisos=[
            'atenciones.ver', 'actividades.ver', 'actividades.editar', 'actividades.ver_equipo',
            'evidencias.ver', 'evidencias.ver_equipo', 'compromisos.ver', 'compromisos.ver_equipo'])
        self.u = Usuario.objects.create_user('progreso', rol=self.role, delegacion=self.d)
        self.other = Usuario.objects.create_user('otro_progreso', rol=self.role, delegacion=self.d)
        self.item = ItemMeta.objects.create(codigo='PROG', nombre='Ítem progreso')
        self.client.force_login(self.u)

    def activity(self, **kw):
        args = dict(autor=self.u, delegacion=self.d, item=self.item, fecha=self.today,
                    solicitud='Actividad propia', accion='Acción', contacto='QA', telefono='912345678', sector='Centro')
        args.update(kw)
        return Actividad.objects.create(**args)

    def evidence(self, activity, **kw):
        args = dict(autor=activity.autor, delegacion=activity.delegacion, actividad=activity,
                    archivo='qa.pdf', nombre_archivo='QA.pdf', tipo_mime='application/pdf', tamano=10,
                    sha256='a' * 64, descripcion='QA')
        args.update(kw)
        return Evidencia.objects.create(**args)

    def commitment(self, **kw):
        args = dict(autor=self.u, responsable=self.u, delegacion=self.d, descripcion='Compromiso propio',
                    solicitante='QA', sector='Centro', area_apoyo='QA', origen='Interno', fecha_comprometida=self.today)
        args.update(kw)
        return Compromiso.objects.create(**args)

    def get_data(self, query=''):
        r = self.client.get('/api/mi-progreso/' + query)
        self.assertEqual(r.status_code, 200)
        return r.json()['data']

    def test_requiere_sesion_y_rol_activo(self):
        self.client.logout()
        self.assertEqual(self.client.get('/api/mi-progreso/').status_code, 401)
        self.client.force_login(self.u)
        self.role.estado = False; self.role.save()
        self.assertEqual(self.client.get('/api/mi-progreso/').status_code, 403)

    def test_resumen_personal_no_confunde_equipo_ni_delegacion(self):
        self.activity(); self.activity(autor=self.other); self.activity(delegacion=self.foreign)
        self.commitment(estado='Realizado')
        self.commitment(autor=self.other, responsable=self.u)
        self.commitment(responsable=self.other)
        data = self.get_data()
        self.assertEqual(data['month']['activities'], 1)
        self.assertEqual(data['month']['commitments'], {'total': 2, 'closed': 1, 'percent': 50})
        self.assertEqual(data['pending']['commitments'], 1)
        self.assertEqual(sum(w['activities'] for w in data['weeks']), 1)

    def test_sin_permisos_no_filtra_registros_ni_titulos(self):
        self.commitment(); self.activity(estado='Corrección')
        self.role.permisos = []; self.role.save()
        data = self.get_data()
        self.assertEqual(data['tasks'], [])
        self.assertEqual(data['month']['activities'], None)
        self.assertEqual(data['month']['commitments'], None)
        self.assertEqual(data['pending']['review'], None)

    def test_evidencias_propias_vigentes_esperan_a_otra_persona(self):
        a = self.activity()
        old = self.evidence(a, estado='Corrección')
        self.evidence(a, reemplaza=old)
        self.evidence(a, estado='Anulada')
        self.evidence(self.activity(autor=self.other))
        data = self.get_data()
        self.assertEqual(data['month']['evidence'], {'approved': 0, 'waiting': 1, 'correction': 0})
        self.assertEqual(data['pending']['review'], None)
        self.assertFalse(any(t['kind'] == 'review' for t in data['tasks']))

    def test_revisor_solo_recibe_pendientes_vigentes_ajenos(self):
        self.role.permisos += ['evidencias.revisar']; self.role.save()
        self.evidence(self.activity())
        foreign = self.activity(autor=self.other)
        valid = self.evidence(foreign)
        self.evidence(foreign, autor=self.u)
        old = self.evidence(foreign)
        self.evidence(foreign, reemplaza=old, estado='Aprobada')
        self.evidence(self.activity(autor=self.other, delegacion=self.foreign))
        data = self.get_data()
        self.assertEqual(data['pending']['review'], 1)
        self.assertEqual([t['id'] for t in data['tasks'] if t['kind'] == 'review'], [valid.pk])

    def test_pendientes_incluyen_antiguos_y_priorizan_vencidos(self):
        late = self.commitment(fecha_comprometida=self.today - timedelta(days=3))
        start = self.today.replace(day=1)
        old = timezone.make_aware(datetime.combine(start - timedelta(days=2), time.min))
        Compromiso.objects.filter(pk=late.pk).update(creado=old)
        self.commitment(fecha_comprometida=self.today + timedelta(days=2))
        self.commitment(fecha_comprometida=self.today - timedelta(days=10), estado='Realizado')
        data = self.get_data()
        self.assertEqual(data['pending']['commitments'], 2)
        self.assertEqual(data['pending']['overdue'], 1)
        self.assertEqual(data['tasks'][0]['id'], late.pk)
        self.assertEqual(data['tasks'][0]['priority'], 'overdue')
        self.assertIn('id=' + str(late.pk), data['tasks'][0]['url'])

    def test_correccion_tiene_acceso_al_registro_y_no_espera_revision(self):
        e = self.evidence(self.activity(), estado='Corrección')
        data = self.get_data()
        task = next(t for t in data['tasks'] if t['kind'] == 'correction')
        self.assertEqual(task['id'], e.pk)
        self.assertIn('registro=' + str(e.pk), task['url'])
        self.assertEqual(data['pending']['correction'], 1)

    def test_mes_limites_semana_y_ceros(self):
        a = self.activity()
        start = self.today.replace(day=1)
        Actividad.objects.filter(pk=a.pk).update(creado=timezone.make_aware(datetime.combine(start, time.min)))
        data = self.get_data()
        self.assertEqual(data['weeks'][0]['activities'], 1)
        self.assertEqual(data['month']['commitments']['percent'], None)
        self.assertEqual(data['month']['commitments']['total'], 0)
        previous = (start - timedelta(days=1)).strftime('%Y-%m')
        self.assertEqual(self.get_data('?mes=' + previous)['month']['activities'], 0)

    def test_mes_invalido_rechaza(self):
        for value in ['2026-13', 'no', '2026-1', '9999-01', '2000-00']:
            self.assertEqual(self.client.get('/api/mi-progreso/', {'mes': value}).status_code, 400)

    def test_rechaza_contexto_sin_delegacion_autorizada(self):
        self.u.delegacion = None; self.u.save()
        self.assertEqual(self.client.get('/api/mi-progreso/').status_code, 403)

    def test_atenciones_personales_no_incluyen_autor_ajeno_ni_otro_contexto(self):
        from .models import Atencion, TipoAtencion, SubAtencion
        kind = TipoAtencion.objects.create(codigo='PG', nombre='Tipo progreso')
        sub = SubAtencion.objects.create(codigo='PG', nombre='Sub progreso', tipo_atencion=kind)
        for n, user, delegation, active in [(1, self.u, self.d, True), (2, self.other, self.d, True),
                                             (3, self.u, self.foreign, True), (4, self.u, self.d, False)]:
            Atencion.objects.create(folio=f'PG-{n}', solicitante='QA', descripcion='QA', tipo_atencion=kind,
                                    sub_atencion=sub, usuario=user, delegacion=delegation, estado=active)
        data = self.get_data()
        self.assertEqual(data['month']['attentions'], 1)
        self.assertEqual(sum(w['attentions'] for w in data['weeks']), 1)

    def test_correcciones_de_actividad_no_duplican_evidencia_y_cache_es_privada(self):
        a = self.activity(estado='Corrección')
        self.evidence(a, estado='Corrección')
        b = self.activity(estado='Rechazada')
        r = self.client.get('/api/mi-progreso/')
        data = r.json()['data']
        self.assertEqual(data['pending']['activity_correction'], 1)
        self.assertEqual([t['id'] for t in data['tasks'] if t['kind'] == 'activity_correction'], [b.pk])
        self.assertEqual(r['Cache-Control'], 'private, no-store')
