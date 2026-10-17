"""Regresión de integración: el frontend no depende de un nombre fijo de cookie."""
from django.test import Client, TestCase, override_settings

class CsrfPortable(TestCase):
    @override_settings(CSRF_COOKIE_NAME='sgr_prueba_cookie')
    def test_token_publicado_usa_cookie_configurada_y_protege_escrituras(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/api/csrf/')
        self.assertEqual(response.status_code, 200)
        token = response.json()['data']['csrfToken']
        self.assertIn('sgr_prueba_cookie', response.cookies)
        self.assertEqual(client.post('/api/login/', {}, content_type='application/json').status_code, 403)
        accepted = client.post('/api/login/', {}, content_type='application/json', HTTP_X_CSRFTOKEN=token)
        self.assertNotEqual(accepted.status_code, 403)
