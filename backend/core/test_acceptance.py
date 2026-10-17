"""Regresiones encontradas durante la aceptación funcional local/AWS."""
from django.test import TestCase
from .models import Usuario, ItemMeta, ConfiguracionMeta


class UnicidadMetaPorPeriodo(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_superuser(
            'aceptacion', 'aceptacion@example.test', 'ClavePruebas!7261'
        )
        self.client.force_login(self.user)
        self.item = ItemMeta.objects.create(codigo='QA-META', nombre='Ítem QA')
        self.meta = ConfiguracionMeta.objects.create(
            item=self.item, periodo='2026-Trimestre 1', meta_esperada=10,
            ponderacion=20,
        )

    def test_no_crear_misma_meta_item_periodo(self):
        response = self.client.post('/api/configuraciones-metas/', {
            'item': self.item.pk, 'periodo': ' 2026-Trimestre 1 ',
            'meta_esperada': 30, 'ponderacion': 40,
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(ConfiguracionMeta.objects.count(), 1)

    def test_no_editar_otro_periodo_para_duplicarlo(self):
        other = ConfiguracionMeta.objects.create(
            item=self.item, periodo='2026-Trimestre 2', meta_esperada=10,
            ponderacion=20,
        )
        response = self.client.patch(f'/api/configuraciones-metas/{other.pk}/', {
            '_version': other.version, 'periodo': '2026-Trimestre 1',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400, response.content)
        other.refresh_from_db()
        self.assertEqual(other.periodo, '2026-Trimestre 2')

    def test_editar_su_meta_y_otro_periodo_sigue_permitido(self):
        response = self.client.patch(f'/api/configuraciones-metas/{self.meta.pk}/', {
            '_version': self.meta.version, 'meta_esperada': 15,
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)
        response = self.client.post('/api/configuraciones-metas/', {
            'item': self.item.pk, 'periodo': '2026-Trimestre 2',
            'meta_esperada': 30, 'ponderacion': 40,
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201, response.content)
