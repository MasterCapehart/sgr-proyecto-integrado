import json
from unittest import expectedFailure

from django.core import mail
from django.test import TestCase, Client

from .models import Rol, Usuario


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


RUTAS_PROTEGIDAS = [
    "/api/roles/", "/api/usuarios/", "/api/tipos-atencion/", "/api/subatenciones/",
    "/api/items-metas/", "/api/atenciones/", "/api/delegaciones/",
    "/api/contexto/", "/api/atenciones/contexto/",
    "/api/roles/export/", "/api/usuarios/export/", "/api/tipos-atencion/export/",
    "/api/subatenciones/export/", "/api/items-metas/export/",
    "/api/atenciones/export/", "/api/delegaciones/export/",
]

RUTAS_DE_ESCRITURA = [
    "/api/roles/", "/api/usuarios/", "/api/tipos-atencion/", "/api/subatenciones/",
    "/api/items-metas/", "/api/delegaciones/", "/api/atenciones/",
]


class SesionTestCase(TestCase):
    CLAVE = "ClaveSegura123!"

    def setUp(self):
        self.rol_admin = Rol.objects.create(nombre="Administrador", descripcion="Acceso total", estado=True)
        self.rol_lector = Rol.objects.create(nombre="Lector", descripcion="Solo consulta", estado=True)
        self.rol_ciudadano = Rol.objects.create(nombre="Ciudadano", descripcion="Sin escritura", estado=True)
        self.admin = Usuario.objects.create_user(
            username="admin_acc", password=self.CLAVE, email="admin_acc@laserena.cl", rol=self.rol_admin
        )
        self.lector = Usuario.objects.create_user(
            username="lector_acc", password=self.CLAVE, email="lector_acc@laserena.cl", rol=self.rol_lector
        )
        self.ciudadano = Usuario.objects.create_user(
            username="ciud_acc", password=self.CLAVE, email="ciud_acc@laserena.cl", rol=self.rol_ciudadano
        )


class LoginLogoutTests(SesionTestCase):
    """T05: inicio y cierre de sesion."""

    def test_login_valido_abre_sesion(self):
        c = Client()
        r = post_json(c, "/api/login/", {"username": "admin_acc", "password": self.CLAVE})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(c.get("/api/roles/").status_code, 200)

    def test_clave_incorrecta_es_401_y_no_abre_sesion(self):
        c = Client()
        r = post_json(c, "/api/login/", {"username": "admin_acc", "password": "incorrecta"})
        self.assertEqual(r.status_code, 401)
        self.assertEqual(c.get("/api/roles/").status_code, 401)

    def test_usuario_inexistente_es_401(self):
        r = post_json(Client(), "/api/login/", {"username": "no_existe", "password": "x"})
        self.assertEqual(r.status_code, 401)

    def test_cuenta_inactiva_no_inicia_sesion(self):
        self.lector.is_active = False
        self.lector.save()
        c = Client()
        r = post_json(c, "/api/login/", {"username": "lector_acc", "password": self.CLAVE})
        self.assertIn(r.status_code, (401, 403))
        self.assertEqual(c.get("/api/roles/").status_code, 401)

    def test_login_con_get_es_405(self):
        self.assertEqual(Client().get("/api/login/").status_code, 405)

    def test_login_con_json_invalido_es_400(self):
        r = Client().post("/api/login/", data="no es json", content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_logout_cierra_la_sesion(self):
        c = Client()
        post_json(c, "/api/login/", {"username": "admin_acc", "password": self.CLAVE})
        self.assertEqual(c.get("/api/roles/").status_code, 200)
        self.assertEqual(c.post("/api/logout/").status_code, 200)
        self.assertEqual(c.get("/api/roles/").status_code, 401)

    def test_logout_con_get_es_405(self):
        self.assertEqual(Client().get("/api/logout/").status_code, 405)

    @expectedFailure
    def test_login_se_bloquea_tras_intentos_fallidos(self):
        """DEFECTO conocido: no hay limite de intentos de login."""
        c = Client()
        for _ in range(10):
            post_json(c, "/api/login/", {"username": "admin_acc", "password": "mala"})
        r = post_json(c, "/api/login/", {"username": "admin_acc", "password": self.CLAVE})
        self.assertNotEqual(r.status_code, 200)


class RutasProtegidasTests(SesionTestCase):
    """T08: ninguna ruta de la API responde sin sesion."""

    def test_rutas_sin_sesion_devuelven_401(self):
        c = Client()
        for ruta in RUTAS_PROTEGIDAS:
            with self.subTest(ruta=ruta):
                self.assertEqual(c.get(ruta).status_code, 401)

    def test_rutas_con_sesion_no_devuelven_401(self):
        c = Client()
        c.force_login(self.admin)
        for ruta in RUTAS_PROTEGIDAS:
            with self.subTest(ruta=ruta):
                self.assertNotEqual(c.get(ruta).status_code, 401)


class PermisosPorRolTests(SesionTestCase):
    """T08/T09/T10: roles de solo lectura no pueden modificar datos."""

    def test_lector_y_ciudadano_no_pueden_escribir(self):
        for usuario in (self.lector, self.ciudadano):
            c = Client()
            c.force_login(usuario)
            for ruta in RUTAS_DE_ESCRITURA:
                with self.subTest(usuario=usuario.username, ruta=ruta):
                    self.assertEqual(post_json(c, ruta, {}).status_code, 403)

    def test_lector_no_puede_activar_ni_eliminar(self):
        c = Client()
        c.force_login(self.lector)
        self.assertEqual(c.post(f"/api/roles/{self.rol_admin.pk}/toggle-estado/").status_code, 403)
        self.assertEqual(c.delete(f"/api/roles/{self.rol_admin.pk}/").status_code, 403)
        self.rol_admin.refresh_from_db()
        self.assertTrue(self.rol_admin.estado)

    def test_lector_si_puede_consultar(self):
        c = Client()
        c.force_login(self.lector)
        self.assertEqual(c.get("/api/roles/").status_code, 200)

    def test_admin_si_puede_escribir(self):
        c = Client()
        c.force_login(self.admin)
        r = post_json(c, "/api/roles/", {"nombre": "Auditor", "descripcion": "Revisa", "estado": True})
        self.assertEqual(r.status_code, 201)


class RecuperacionTests(SesionTestCase):
    """T06/T07: recuperacion de contrasena por codigo."""

    def pedir_codigo(self, email="admin_acc@laserena.cl"):
        post_json(Client(), "/api/recuperacion/", {"email": email})
        return Usuario.objects.get(email=email).codigo_recuperacion

    def test_solicitar_genera_codigo_de_6_digitos_y_envia_correo(self):
        codigo = self.pedir_codigo()
        self.assertIsNotNone(codigo)
        self.assertEqual(len(codigo), 6)
        self.assertTrue(codigo.isdigit())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["admin_acc@laserena.cl"])

    def test_correo_inexistente_responde_igual_y_no_envia(self):
        r_ok = post_json(Client(), "/api/recuperacion/", {"email": "admin_acc@laserena.cl"})
        r_no = post_json(Client(), "/api/recuperacion/", {"email": "nadie@laserena.cl"})
        self.assertEqual(r_ok.status_code, 200)
        self.assertEqual(r_no.status_code, 200)
        self.assertEqual(r_ok.json(), r_no.json())
        self.assertEqual(len(mail.outbox), 1)

    def test_solicitar_sin_correo_es_400(self):
        self.assertEqual(post_json(Client(), "/api/recuperacion/", {}).status_code, 400)

    def test_codigo_correcto_cambia_la_clave(self):
        codigo = self.pedir_codigo()
        r = post_json(Client(), "/api/validar-recuperacion/", {
            "email": "admin_acc@laserena.cl", "codigo": codigo, "nueva_password": "OtraClave456!",
        })
        self.assertEqual(r.status_code, 200)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password("OtraClave456!"))
        self.assertFalse(self.admin.check_password(self.CLAVE))

    def test_codigo_es_de_un_solo_uso(self):
        codigo = self.pedir_codigo()
        datos = {"email": "admin_acc@laserena.cl", "codigo": codigo, "nueva_password": "OtraClave456!"}
        self.assertEqual(post_json(Client(), "/api/validar-recuperacion/", datos).status_code, 200)
        datos["nueva_password"] = "TerceraClave789!"
        self.assertEqual(post_json(Client(), "/api/validar-recuperacion/", datos).status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password("OtraClave456!"))

    def test_codigo_incorrecto_no_cambia_la_clave(self):
        self.pedir_codigo()
        r = post_json(Client(), "/api/validar-recuperacion/", {
            "email": "admin_acc@laserena.cl", "codigo": "000000", "nueva_password": "OtraClave456!",
        })
        self.assertEqual(r.status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password(self.CLAVE))

    def test_faltan_datos_es_400(self):
        r = post_json(Client(), "/api/validar-recuperacion/", {"email": "admin_acc@laserena.cl"})
        self.assertEqual(r.status_code, 400)

    def test_reenvio_invalida_el_codigo_anterior(self):
        primero = self.pedir_codigo()
        segundo = self.pedir_codigo()
        if primero == segundo:
            self.skipTest("El azar repitio el mismo codigo; se vuelve a ejecutar sin problema.")
        r = post_json(Client(), "/api/validar-recuperacion/", {
            "email": "admin_acc@laserena.cl", "codigo": primero, "nueva_password": "OtraClave456!",
        })
        self.assertEqual(r.status_code, 400)

    @expectedFailure
    def test_codigo_se_invalida_tras_intentos_fallidos(self):
        """DEFECTO conocido: no hay limite de intentos al validar el codigo."""
        codigo = self.pedir_codigo()
        for _ in range(5):
            post_json(Client(), "/api/validar-recuperacion/", {
                "email": "admin_acc@laserena.cl", "codigo": "000000", "nueva_password": "OtraClave456!",
            })
        r = post_json(Client(), "/api/validar-recuperacion/", {
            "email": "admin_acc@laserena.cl", "codigo": codigo, "nueva_password": "OtraClave456!",
        })
        self.assertEqual(r.status_code, 400)

    @expectedFailure
    def test_contrasena_debil_se_rechaza(self):
        """DEFECTO conocido: la contrasena nueva no se valida."""
        codigo = self.pedir_codigo()
        r = post_json(Client(), "/api/validar-recuperacion/", {
            "email": "admin_acc@laserena.cl", "codigo": codigo, "nueva_password": "1",
        })
        self.assertEqual(r.status_code, 400)