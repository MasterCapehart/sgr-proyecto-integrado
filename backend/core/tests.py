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

    # =======================================================
    # Pruebas Específicas T14: Reglas de Negocio e Integridad
    # =======================================================

    def test_create_duplicate_codigo_rejected(self):
        """T14: Verifica que se rechacen códigos duplicados en Tipos de Atención."""
        payload = {
            "codigo": "TA-01",  # Ya existe en setUp
            "nombre": "Nombre Nuevo Único",
            "descripcion": "Descripción",
            "estado": True
        }
        response = self.client.post(
            "/api/tipos-atencion/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("codigo", data["error"]["details"])

    def test_create_duplicate_nombre_rejected(self):
        """T14: Verifica que se rechacen nombres duplicados en Tipos de Atención."""
        payload = {
            "codigo": "TA-NUEVO-99",
            "nombre": "Tipo Atención 1",  # Ya existe en setUp
            "descripcion": "Descripción",
            "estado": True
        }
        response = self.client.post(
            "/api/tipos-atencion/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("nombre", data["error"]["details"])

    def test_reject_deactivation_with_active_subatenciones(self):
        """T14: Impide desactivar catálogo padre si posee subatenciones activas asociadas."""
        from .models import SubAtencion
        parent = TipoAtencion.objects.filter(estado=True).first()
        
        # Crear subatención hija activa
        SubAtencion.objects.create(
            tipo_atencion=parent,
            codigo="SUB-01",
            nombre="Subatención de Prueba",
            descripcion="Hija activa",
            estado=True
        )

        # Intentar desactivar el padre mediante DELETE
        res_del = self.client.delete(f"/api/tipos-atencion/{parent.pk}/")
        self.assertEqual(res_del.status_code, 400)
        data_del = res_del.json()
        self.assertFalse(data_del["success"])
        self.assertEqual(data_del["error"]["code"], "HAS_ACTIVE_DEPENDENCIES")

        # Intentar desactivar el padre mediante toggle-estado
        res_toggle = self.client.post(f"/api/tipos-atencion/{parent.pk}/toggle-estado/")
        self.assertEqual(res_toggle.status_code, 400)
        data_toggle = res_toggle.json()
        self.assertFalse(data_toggle["success"])
        self.assertEqual(data_toggle["error"]["code"], "HAS_ACTIVE_DEPENDENCIES")

    def test_allow_deactivation_when_subatenciones_inactive(self):
        """T14: Permite desactivar el catálogo padre cuando todas sus subatenciones están inactivas."""
        from .models import SubAtencion
        parent = TipoAtencion.objects.filter(estado=True).first()
        
        # Crear subatención hija inactiva
        SubAtencion.objects.create(
            tipo_atencion=parent,
            codigo="SUB-INACTIVA",
            nombre="Subatención Inactiva",
            descripcion="Hija inactiva",
            estado=False
        )

        # Ahora la desactivación del padre debe permitirse
        res_del = self.client.delete(f"/api/tipos-atencion/{parent.pk}/")
        self.assertEqual(res_del.status_code, 200)
        parent.refresh_from_db()
        self.assertFalse(parent.estado)

    def test_export_tipos_atencion_csv(self):
        """T14: Verifica la exportación común de Tipos de Atención a CSV descargable."""
        response = self.client.get("/api/tipos-atencion/export/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("tipoatencion_export.csv", response["Content-Disposition"])
        content = response.content.decode("utf-8-sig")
        self.assertIn("Código", content)
        self.assertIn("Nombre", content)

    # =======================================================
    # Pruebas Específicas T15: Catálogo Hijo SubAtencion
    # =======================================================

    def test_subatencion_list_with_parent_display(self):
        """T15: Verifica que el listado de subatenciones incluya la información del tipo padre."""
        parent = TipoAtencion.objects.filter(estado=True).first()
        from .models import SubAtencion
        sub = SubAtencion.objects.create(
            tipo_atencion=parent,
            codigo="SA-TEST-01",
            nombre="Subatención Test",
            estado=True
        )

        response = self.client.get("/api/subatenciones/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        
        found = next((item for item in data["results"] if item["codigo"] == "SA-TEST-01"), None)
        self.assertIsNotNone(found)
        self.assertEqual(found["tipo_atencion"], parent.pk)
        self.assertEqual(found["tipo_padre_display"], f"{parent.codigo} · {parent.nombre}")

    def test_subatencion_search_by_parent_name(self):
        """T15: Verifica la búsqueda de subatenciones filtrando por el nombre del catálogo padre."""
        parent = TipoAtencion.objects.filter(estado=True).first()
        from .models import SubAtencion
        SubAtencion.objects.create(
            tipo_atencion=parent,
            codigo="SA-SEARCH-01",
            nombre="Búsqueda Especializada",
            estado=True
        )

        response = self.client.get(f"/api/subatenciones/?search={parent.nombre}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(any(item["codigo"] == "SA-SEARCH-01" for item in data["results"]))

    def test_subatencion_create_success_with_active_parent(self):
        """T15: Verifica creación exitosa de subatención asociando un catálogo padre activo."""
        parent = TipoAtencion.objects.filter(estado=True).first()
        payload = {
            "codigo": "SA-NUEVA-01",
            "nombre": "Nueva Subatención Exitosa",
            "tipo_atencion": parent.pk,
            "estado": True
        }
        response = self.client.post(
            "/api/subatenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["codigo"], "SA-NUEVA-01")
        self.assertEqual(data["data"]["tipo_atencion"], parent.pk)

    def test_subatencion_create_inactive_parent_rejected(self):
        """T15: Rechaza asociar una subatención a un tipo de atención inactivo (Regla T15)."""
        inactive_parent = TipoAtencion.objects.filter(estado=False).first()
        payload = {
            "codigo": "SA-RECHAZADA",
            "nombre": "Subatención con Padre Inactivo",
            "tipo_atencion": inactive_parent.pk,
            "estado": True
        }
        response = self.client.post(
            "/api/subatenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("tipo_atencion", data["error"]["details"])

    def test_subatencion_create_missing_parent_rejected(self):
        """T15: Rechaza crear una subatención sin indicar catálogo padre."""
        payload = {
            "codigo": "SA-SIN-PADRE",
            "nombre": "Subatención Huérfana",
            "estado": True
        }
        response = self.client.post(
            "/api/subatenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("tipo_atencion", data["error"]["details"])

    def test_subatencion_duplicate_codigo_rejected(self):
        """T15: Rechaza código de subatención duplicado."""
        parent = TipoAtencion.objects.filter(estado=True).first()
        from .models import SubAtencion
        SubAtencion.objects.create(
            tipo_atencion=parent,
            codigo="SA-DUP-01",
            nombre="Nombre Original",
            estado=True
        )

        payload = {
            "codigo": "SA-DUP-01",
            "nombre": "Otro Nombre",
            "tipo_atencion": parent.pk,
            "estado": True
        }
        response = self.client.post(
            "/api/subatenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("codigo", data["error"]["details"])

    def test_subatencion_duplicate_nombre_under_same_parent_rejected(self):
        """T15: Rechaza nombre duplicado bajo el mismo catálogo padre."""
        parent = TipoAtencion.objects.filter(estado=True).first()
        from .models import SubAtencion
        SubAtencion.objects.create(
            tipo_atencion=parent,
            codigo="SA-NOM-01",
            nombre="Nombre Repetido",
            estado=True
        )

        payload = {
            "codigo": "SA-NOM-02",
            "nombre": "Nombre Repetido",
            "tipo_atencion": parent.pk,
            "estado": True
        }
        response = self.client.post(
            "/api/subatenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("nombre", data["error"]["details"])

    def test_subatencion_toggle_estado(self):
        """T15: Verifica alternar estado activo/inactivo de una subatención."""
        parent = TipoAtencion.objects.filter(estado=True).first()
        from .models import SubAtencion
        sub = SubAtencion.objects.create(
            tipo_atencion=parent,
            codigo="SA-TOGGLE-01",
            nombre="Sub Toggle",
            estado=True
        )

        response = self.client.post(f"/api/subatenciones/{sub.pk}/toggle-estado/")
        self.assertEqual(response.status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.estado)

    def test_subatencion_export_csv(self):
        """T15: Verifica la exportación común de Subatenciones a CSV."""
        response = self.client.get("/api/subatenciones/export/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("subatenciones_export.csv", response["Content-Disposition"])
        content = response.content.decode("utf-8-sig")
        self.assertIn("Tipo de Atención Padre", content)


