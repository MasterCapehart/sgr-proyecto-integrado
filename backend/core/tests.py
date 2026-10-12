import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import TipoAtencion, Delegacion


class PatronCRUDAPITestCase(TestCase):
    """
    Pruebas automatizadas del Patrón Común de CRUD para la API (Tarea T04).
    Verifica entradas, respuestas, paginación, filtros, errores y reusabilidad.
    """

    def setUp(self):
        self.client = Client()
        
        # Crear datos de prueba para TipoAtencion
        for i in range(1, 16):
            TipoAtencion.objects.create(
                codigo=f"TA-{i:02d}",
                nombre=f"Tipo Atención {i}",
                descripcion=f"Descripción para el tipo {i}",
                estado=(i % 2 != 0)  # Impares activos, pares inactivos
            )

    def test_list_pagination_default(self):
        """Verifica paginación por defecto (10 elementos por página y estructura de sobre)."""
        response = self.client.get("/api/tipos-atencion/?estado=todos")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 15)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 10)
        self.assertEqual(data["total_pages"], 2)
        self.assertEqual(len(data["results"]), 10)

    def test_list_filter_by_estado(self):
        """Verifica filtrado por estado (activos por defecto o explícito)."""
        # Solo activos
        response_activos = self.client.get("/api/tipos-atencion/?estado=activos")
        data_activos = response_activos.json()
        self.assertTrue(data_activos["success"])
        self.assertEqual(data_activos["count"], 8)  # 1, 3, 5, 7, 9, 11, 13, 15
        for item in data_activos["results"]:
            self.assertTrue(item["estado"])

        # Solo inactivos
        response_inactivos = self.client.get("/api/tipos-atencion/?estado=inactivos")
        data_inactivos = response_inactivos.json()
        self.assertTrue(data_inactivos["success"])
        self.assertEqual(data_inactivos["count"], 7)  # 2, 4, 6, 8, 10, 12, 14
        for item in data_inactivos["results"]:
            self.assertFalse(item["estado"])

    def test_list_search_query(self):
        """Verifica búsqueda por texto libre con ?search=."""
        response = self.client.get("/api/tipos-atencion/?search=TA-05&estado=todos")
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["codigo"], "TA-05")

    def test_retrieve_detail_success(self):
        """Verifica detalle de un registro existente."""
        item = TipoAtencion.objects.first()
        response = self.client.get(f"/api/tipos-atencion/{item.pk}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], item.pk)
        self.assertEqual(data["data"]["codigo"], item.codigo)

    def test_retrieve_not_found(self):
        """Verifica respuesta 404 estructurada cuando el ID no existe."""
        response = self.client.get("/api/tipos-atencion/99999/")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "NOT_FOUND")

    def test_create_success(self):
        """Verifica creación de nuevo registro mediante POST con JSON."""
        payload = {
            "codigo": "TA-NUEVO",
            "nombre": "Atención Jurídica",
            "descripcion": "Asesoría legal municipal",
            "estado": True
        }
        response = self.client.post(
            "/api/tipos-atencion/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["codigo"], "TA-NUEVO")
        self.assertTrue(TipoAtencion.objects.filter(codigo="TA-NUEVO").exists())

    def test_create_validation_error_missing_field(self):
        """Verifica error 400 estructurado al omitir campos requeridos."""
        payload = {
            "descripcion": "Falta código y nombre"
        }
        response = self.client.post(
            "/api/tipos-atencion/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("codigo", data["error"]["details"])
        self.assertIn("nombre", data["error"]["details"])

    def test_update_patch_success(self):
        """Verifica actualización parcial mediante PATCH."""
        item = TipoAtencion.objects.first()
        payload = {"nombre": "Nombre Actualizado"}
        response = self.client.patch(
            f"/api/tipos-atencion/{item.pk}/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["nombre"], "Nombre Actualizado")
        item.refresh_from_db()
        self.assertEqual(item.nombre, "Nombre Actualizado")

    def test_soft_delete(self):
        """Verifica que DELETE realiza una desactivación lógica (estado = False)."""
        item = TipoAtencion.objects.filter(estado=True).first()
        response = self.client.delete(f"/api/tipos-atencion/{item.pk}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        item.refresh_from_db()
        self.assertFalse(item.estado)

    def test_toggle_estado(self):
        """Verifica que /toggle-estado/ alterna correctamente entre activo e inactivo."""
        item = TipoAtencion.objects.filter(estado=True).first()
        response = self.client.post(f"/api/tipos-atencion/{item.pk}/toggle-estado/")
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertFalse(item.estado)

        # Alternar de vuelta a True
        response2 = self.client.post(f"/api/tipos-atencion/{item.pk}/toggle-estado/")
        self.assertEqual(response2.status_code, 200)
        item.refresh_from_db()
        self.assertTrue(item.estado)

    def test_reusability_delegacion_crud(self):
        """Verifica que el patrón común aplica de forma idéntica a Delegaciones (para Matías T13)."""
        # Crear delegación
        payload = {
            "nombre": "Delegación Rural Norte",
            "direccion": "Camino Vecinal 123",
            "comuna": "La Serena",
            "estado": True
        }
        res_create = self.client.post(
            "/api/delegaciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res_create.status_code, 201)
        data_create = res_create.json()
        self.assertEqual(data_create["data"]["nombre"], "Delegación Rural Norte")

        # Listar con búsqueda
        res_list = self.client.get("/api/delegaciones/?search=Rural")
        self.assertEqual(res_list.status_code, 200)
        data_list = res_list.json()
        self.assertEqual(data_list["count"], 1)
        self.assertEqual(data_list["results"][0]["nombre"], "Delegación Rural Norte")
