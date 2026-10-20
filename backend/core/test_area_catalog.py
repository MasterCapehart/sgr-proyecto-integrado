import json
from django.test import TestCase
from .models import Cargo, Delegacion, Rol, Usuario, EventoLocal, VersionCatalogo, ItemMeta


class AreasExcelTests(TestCase):
    url = '/api/cargos/referencia-excel/'

    def setUp(self):
        self.d = Delegacion.objects.create(codigo='AREA', nombre='Delegación QA')
        self.admin = Usuario.objects.create_superuser('admin_areas', 'areas@example.test', 'PruebaLocal!937', delegacion=self.d, first_name='Admin QA')
        self.client.force_login(self.admin)

    def post(self, data=None):
        return self.client.post(self.url, json.dumps({'confirmar': True} if data is None else data), content_type='application/json')

    def test_previsualiza_doce_entradas_sin_crear_registros(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        data = r.json()['data']
        self.assertEqual(len(data['entries']), 12)
        self.assertEqual(data['summary']['create'], 12)
        self.assertEqual(Cargo.objects.count(), 0)
        self.assertEqual({x['nombre'] for x in data['entries'] if x['planilla'] == 'G_SOC'}, {f'GESTOR SOCIAL {i}' for i in range(1, 6)})
        self.assertEqual({x['nombre'] for x in data['entries'] if x['planilla'] == 'T_OC'}, {f'TERRITORIAL OO.CC. {i}' for i in range(1, 5)})
        self.assertNotIn('GES_SEG', {x['planilla'] for x in data['entries']})

    def test_incorpora_sin_reasignar_personas_ni_roles_ni_items(self):
        old = Cargo.objects.create(codigo='LEGACY', nombre='Cargo anterior', area='Área anterior', planilla='AP_ADM')
        self.admin.cargo = old; self.admin.save()
        item = ItemMeta.objects.create(codigo='AREA', nombre='Ítem anterior'); item.cargos.add(old)
        r = self.post()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['data']['created'], 12)
        self.assertEqual(Cargo.objects.count(), 13)
        self.admin.refresh_from_db();self.assertEqual(self.admin.cargo_id, old.pk)
        self.assertEqual(list(item.cargos.values_list('pk', flat=True)), [old.pk])
        self.assertTrue(self.admin.is_superuser)
        self.assertEqual(Rol.objects.count(), 0)

    def test_repetir_no_duplica_registros_ni_auditoria(self):
        self.assertEqual(self.post().status_code, 200)
        count = EventoLocal.objects.count()
        r = self.post();self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['data']['created'], 0)
        self.assertEqual(Cargo.objects.count(), 12)
        self.assertEqual(EventoLocal.objects.count(), count)

    def test_existente_compatible_se_conserva_incluso_inactivo(self):
        old = Cargo.objects.create(codigo='PERSONALIZADO', nombre='APOYO ADMINISTRATIVO', area='Área previamente acordada', planilla='AP_ADM', estado=False)
        r = self.post();self.assertEqual(r.status_code, 200)
        old.refresh_from_db();self.assertEqual(old.area, 'Área previamente acordada');self.assertFalse(old.estado)
        self.assertEqual(old.version, 1)
        self.assertEqual(r.json()['data']['created'], 11)
        self.assertEqual(Cargo.objects.filter(nombre__iexact='APOYO ADMINISTRATIVO').count(), 1)

    def test_nombre_existente_incompatible_aborta_todo(self):
        Cargo.objects.create(codigo='EXISTE', nombre='GESTOR SOCIAL 3', area='Otra', planilla='AP_ADM')
        r = self.post();self.assertEqual(r.status_code, 409)
        self.assertEqual(Cargo.objects.count(), 1)
        self.assertEqual(EventoLocal.objects.count(), 0)

    def test_codigo_ocupado_por_otro_nombre_no_se_sobrescribe(self):
        preview = self.client.get(self.url)
        self.assertEqual(preview.status_code, 200)
        entry = preview.json()['data']['entries'][0]
        Cargo.objects.create(codigo=entry['codigo'], nombre='Otro nombre', area='Otra', planilla=entry['planilla'])
        self.assertEqual(self.post().status_code, 409)
        self.assertEqual(Cargo.objects.count(), 1)

    def test_cada_alta_conserva_auditoria_y_version_catalogo(self):
        self.assertEqual(self.post().status_code, 200)
        self.assertEqual(EventoLocal.objects.filter(recurso='cargos', accion='crear').count(), 12)
        self.assertEqual(VersionCatalogo.objects.filter(recurso='cargos').count(), 12)
        event = EventoLocal.objects.first()
        self.assertEqual(event.usuario_id, self.admin.pk)
        self.assertEqual(event.delegacion_id, self.d.pk)
        self.assertIn('origen_excel', event.despues)

    def test_exige_sesion_permiso_y_confirmacion(self):
        self.client.logout();self.assertEqual(self.client.get(self.url).status_code, 401)
        role = Rol.objects.create(nombre='Consulta áreas', permisos=['cargos.ver'])
        u = Usuario.objects.create_user('consulta_areas', rol=role, delegacion=self.d)
        self.client.force_login(u)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(self.post().status_code, 403)
        role.permisos = [];role.save()
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.client.force_login(self.admin)
        for invalid in [{}, {'confirmar':False}, {'confirmar':1}, {'confirmar':'true'}, {'confirmar':True,'nombre':'Inventado'}]:
            self.assertEqual(self.post(invalid).status_code, 400)
        self.assertEqual(Cargo.objects.count(), 0)

    def test_asignar_area_no_cambia_el_rol_y_activa_su_planilla(self):
        self.assertEqual(self.post().status_code, 200)
        role = Rol.objects.create(nombre='Funcionario QA áreas', permisos=['actividades.ver'])
        user = Usuario.objects.create_user('funcionario_areas', email='func_area@example.test', first_name='Usuario QA', rol=role, delegacion=self.d)
        user.delegaciones.add(self.d)
        cargo = Cargo.objects.get(nombre='GESTOR SOCIAL 2')
        r = self.client.patch(f'/api/usuarios/{user.pk}/', json.dumps({'cargo':cargo.pk, '_version':user.version}), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        user.refresh_from_db();self.assertEqual(user.cargo_id, cargo.pk);self.assertEqual(user.rol_id, role.pk)
        self.client.force_login(user)
        self.assertEqual(self.client.get('/api/planillas/').json()['asignada'], 'G_SOC')
        context = self.client.get('/api/contexto/').json()['data']
        self.assertEqual(context['usuario']['cargo_nombre'], 'GESTOR SOCIAL 2')
        self.assertEqual(context['permisos'], ['actividades.ver'])
