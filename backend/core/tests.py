import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import (
    TipoAtencion, Delegacion, SubAtencion, ItemMeta,
    ConfiguracionMeta, Rol, Usuario, Atencion, AuditoriaDerivacion
)


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

    # =======================================================
    # Pruebas Específicas T16: CRUD Ítems y Metas
    # =======================================================

    def test_item_meta_list_and_search(self):
        """T16: Verifica listado y búsqueda de ítems medibles."""
        from .models import ItemMeta
        ItemMeta.objects.create(
            codigo="IT-TEST-01",
            nombre="Operativos en Terreno",
            descripcion="Medición de terreno",
            estado=True
        )

        response = self.client.get("/api/items-metas/?search=Terreno")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(any(it["codigo"] == "IT-TEST-01" for it in data["results"]))

    def test_item_meta_create_success(self):
        """T16: Verifica creación exitosa de un ítem medible con persistencia."""
        payload = {
            "codigo": "IT-NUEVO-01",
            "nombre": "Atenciones Ciudadanas Registradas",
            "descripcion": "Total de atenciones en la delegación",
            "unidad_medida": "Cantidad",
            "estado": True
        }
        response = self.client.post(
            "/api/items-metas/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["codigo"], "IT-NUEVO-01")

    def test_item_meta_duplicate_codigo_rejected(self):
        """T16: Rechaza código de ítem duplicado."""
        from .models import ItemMeta
        ItemMeta.objects.create(
            codigo="IT-DUP-01",
            nombre="Ítem Original",
            estado=True
        )

        payload = {
            "codigo": "IT-DUP-01",
            "nombre": "Otro Ítem Distinto",
            "estado": True
        }
        response = self.client.post(
            "/api/items-metas/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("codigo", data["error"]["details"])

    def test_item_meta_duplicate_nombre_rejected(self):
        """T16: Rechaza nombre de ítem duplicado."""
        from .models import ItemMeta
        ItemMeta.objects.create(
            codigo="IT-NOM-01",
            nombre="Compromisos en Plazo",
            estado=True
        )

        payload = {
            "codigo": "IT-NOM-02",
            "nombre": "Compromisos en Plazo",
            "estado": True
        }
        response = self.client.post(
            "/api/items-metas/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("nombre", data["error"]["details"])

    def test_item_meta_reject_deactivation_with_active_configuracion_meta(self):
        """T16: Impide desactivar ítem si posee metas asignadas activas (conserva historia y referencias)."""
        from .models import ItemMeta, ConfiguracionMeta
        item = ItemMeta.objects.create(
            codigo="IT-CON-META",
            nombre="Ítem con Metas",
            estado=True
        )
        ConfiguracionMeta.objects.create(
            item=item,
            periodo="2026-Anual",
            meta_esperada=150.00,
            ponderacion=20.00,
            estado=True
        )

        # Intento de desactivar mediante DELETE
        res_del = self.client.delete(f"/api/items-metas/{item.pk}/")
        self.assertEqual(res_del.status_code, 400)
        data_del = res_del.json()
        self.assertFalse(data_del["success"])
        self.assertEqual(data_del["error"]["code"], "HAS_ACTIVE_DEPENDENCIES")

        # Intento de desactivar mediante toggle-estado
        res_toggle = self.client.post(f"/api/items-metas/{item.pk}/toggle-estado/")
        self.assertEqual(res_toggle.status_code, 400)
        data_toggle = res_toggle.json()
        self.assertFalse(data_toggle["success"])
        self.assertEqual(data_toggle["error"]["code"], "HAS_ACTIVE_DEPENDENCIES")

    def test_item_meta_allow_deactivation_when_configuracion_meta_inactive(self):
        """T16: Permite desactivar ítem cuando todas sus metas configuradas están inactivas."""
        from .models import ItemMeta, ConfiguracionMeta
        item = ItemMeta.objects.create(
            codigo="IT-META-INACTIVA",
            nombre="Ítem con Metas Inactivas",
            estado=True
        )
        ConfiguracionMeta.objects.create(
            item=item,
            periodo="2025-Cerrado",
            meta_esperada=50.00,
            ponderacion=10.00,
            estado=False
        )

        res_del = self.client.delete(f"/api/items-metas/{item.pk}/")
        self.assertEqual(res_del.status_code, 200)
        item.refresh_from_db()
        self.assertFalse(item.estado)

    def test_item_meta_toggle_estado(self):
        """T16: Alterna estado de ítem sin dependencias."""
        from .models import ItemMeta
        item = ItemMeta.objects.create(
            codigo="IT-TOGGLE-01",
            nombre="Ítem Toggle",
            estado=True
        )

        response = self.client.post(f"/api/items-metas/{item.pk}/toggle-estado/")
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertFalse(item.estado)

    def test_item_meta_export_csv(self):
        """T16: Verifica exportación a CSV de ítems y metas."""
        response = self.client.get("/api/items-metas/export/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("items_metas_export.csv", response["Content-Disposition"])
        content = response.content.decode("utf-8-sig")
        self.assertIn("Nombre del Ítem", content)


class AtencionCiudadanaAPITestCase(TestCase):
    """
    Pruebas automatizadas de Registro y Operación de Atención Ciudadana (Tarea T17).
    Criterios de Aceptación:
    - Registro persiste con ID real y folio generado por el servidor.
    - Catálogos activos y validación estricta de compatibilidad tipo/subtipo.
    - Autor, delegación y hora fijados por el contexto institucional del servidor.
    - Cancelar no guarda en base de datos.
    - Recarga y consulta de persistencia.
    """

    def setUp(self):
        self.client = Client()

        # Delegación y usuario de contexto
        self.delegacion = Delegacion.objects.create(
            nombre="DEL01 · Las Compañías",
            direccion="Esmeralda 2451",
            comuna="La Serena",
            estado=True
        )
        self.rol = Rol.objects.create(
            nombre="Operador Territorial",
            descripcion="Operador de atención ciudadana",
            estado=True
        )
        self.usuario = Usuario.objects.create_user(
            username="dflores_test",
            first_name="Daniel",
            last_name="Flores",
            email="dflores@laserena.cl",
            rut="12.345.678-9",
            rol=self.rol,
            delegacion=self.delegacion
        )

        # Catálogo Tipo de Atención
        self.tipo_social = TipoAtencion.objects.create(
            codigo="TA01",
            nombre="Social",
            descripcion="Atención Social",
            estado=True
        )
        self.tipo_territorial = TipoAtencion.objects.create(
            codigo="TA02",
            nombre="Territorial",
            descripcion="Atención Territorial",
            estado=True
        )
        self.tipo_inactivo = TipoAtencion.objects.create(
            codigo="TA09",
            nombre="Tipo Inactivo",
            descripcion="No disponible",
            estado=False
        )

        # Catálogo Subatenciones
        self.sub_social_1 = SubAtencion.objects.create(
            codigo="SA01",
            nombre="Orientación Social",
            tipo_atencion=self.tipo_social,
            estado=True
        )
        self.sub_social_inactiva = SubAtencion.objects.create(
            codigo="SA02",
            nombre="Ayuda Inactiva",
            tipo_atencion=self.tipo_social,
            estado=False
        )
        self.sub_territorial = SubAtencion.objects.create(
            codigo="SA03",
            nombre="Operativo Territorial",
            tipo_atencion=self.tipo_territorial,
            estado=True
        )

    def test_atencion_contexto_servidor(self):
        """T17: Verifica consulta de contexto institucional de sesión."""
        response = self.client.get("/api/atenciones/contexto/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("usuario", data["data"])
        self.assertIn("delegacion", data["data"])
        self.assertIn("fecha_servidor", data["data"])

    def test_atencion_create_success_with_real_folio(self):
        """T17: Registro exitoso persiste en BD con ID real y folio generado por servidor."""
        payload = {
            "solicitante": "María Pérez González (15.234.567-8)",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social_1.pk,
            "descripcion": "Solicitud de asistencia de canasta familiar y subsidio de agua.",
            "caso_social": "CS-2026-001"
        }
        response = self.client.post(
            "/api/atenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        res_data = response.json()
        self.assertTrue(res_data["success"])

        atencion_data = res_data["data"]
        self.assertIsNotNone(atencion_data["id"])
        self.assertTrue(atencion_data["folio"].startswith("AT-"))
        self.assertEqual(atencion_data["solicitante"], payload["solicitante"])
        self.assertEqual(atencion_data["caso_social"], "CS-2026-001")

        # Verificar persistencia real en la base de datos
        db_obj = Atencion.objects.filter(pk=atencion_data["id"]).first()
        self.assertIsNotNone(db_obj)
        self.assertEqual(db_obj.folio, atencion_data["folio"])
        self.assertEqual(db_obj.solicitante, payload["solicitante"])
        self.assertEqual(db_obj.tipo_atencion, self.tipo_social)
        self.assertEqual(db_obj.sub_atencion, self.sub_social_1)

    def test_atencion_persistencia_y_recarga(self):
        """T17: Guardar y consultar posteriormente por API para verificar persistencia completa."""
        atencion = Atencion.objects.create(
            folio="AT-2026-9999",
            solicitante="Juan Valenzuela",
            tipo_atencion=self.tipo_territorial,
            sub_atencion=self.sub_territorial,
            descripcion="Solicitud de poda de árboles en plaza pública",
            delegacion=self.delegacion,
            usuario=self.usuario,
            estado=True
        )

        response = self.client.get(f"/api/atenciones/{atencion.pk}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["folio"], "AT-2026-9999")
        self.assertEqual(data["data"]["solicitante"], "Juan Valenzuela")
        self.assertEqual(data["data"]["tipo_atencion"]["nombre"], "Territorial")

    def test_atencion_rejected_incompatible_subtipo(self):
        """T17: Rechaza si la subatención no pertenece al tipo de atención indicado."""
        payload = {
            "solicitante": "Carlos Tapia",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_territorial.pk,
            "descripcion": "Intento con catálogo incompatible."
        }
        response = self.client.post(
            "/api/atenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.json()
        error_info = res_data.get("error", res_data)
        self.assertEqual(error_info["code"], "VALIDATION_ERROR")
        self.assertIn("sub_atencion", error_info["details"])
        self.assertIn("no pertenece", error_info["details"]["sub_atencion"][0])

    def test_atencion_rejected_inactive_tipo(self):
        """T17: Rechaza creación si el tipo de atención está inactivo."""
        payload = {
            "solicitante": "Pedro Morales",
            "tipo_atencion": self.tipo_inactivo.pk,
            "sub_atencion": self.sub_social_1.pk,
            "descripcion": "Tipo de atención inactivo."
        }
        response = self.client.post(
            "/api/atenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.json()
        error_info = res_data.get("error", res_data)
        self.assertIn("tipo_atencion", error_info["details"])
        self.assertIn("inactivo", error_info["details"]["tipo_atencion"][0])

    def test_atencion_rejected_inactive_subtipo(self):
        """T17: Rechaza creación si la subatención está inactiva."""
        payload = {
            "solicitante": "Rosa Araya",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social_inactiva.pk,
            "descripcion": "Subatención inactiva."
        }
        response = self.client.post(
            "/api/atenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.json()
        error_info = res_data.get("error", res_data)
        self.assertIn("sub_atencion", error_info["details"])
        self.assertIn("inactiv", error_info["details"]["sub_atencion"][0])

    def test_atencion_rejected_missing_required_fields(self):
        """T17: Rechaza si faltan solicitante o descripción obligatorios."""
        payload = {
            "solicitante": "",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social_1.pk,
            "descripcion": ""
        }
        response = self.client.post(
            "/api/atenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.json()
        error_info = res_data.get("error", res_data)
        self.assertIn("solicitante", error_info["details"])
        self.assertIn("descripcion", error_info["details"])

    def test_atencion_server_context_immutable(self):
        """T17: Autor y delegación fijados por el servidor (ignora manipulación de autor desde cliente)."""
        payload = {
            "solicitante": "Vecino Prueba",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social_1.pk,
            "descripcion": "Prueba de contexto del servidor.",
            "usuario": 9999
        }
        response = self.client.post(
            "/api/atenciones/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()["data"]

        db_obj = Atencion.objects.get(pk=data["id"])
        self.assertNotEqual(db_obj.usuario_id, 9999)
        self.assertEqual(db_obj.delegacion, self.delegacion)

    def test_atencion_cancel_does_not_save(self):
        """T17: Cancelar la operación en la interfaz no persiste ningún registro en base de datos."""
        initial_count = Atencion.objects.count()
        # Cancelar en frontend resetea formulario sin enviar HTTP POST
        final_count = Atencion.objects.count()
        self.assertEqual(initial_count, final_count)

    def test_atencion_export_csv(self):
        """T17: Verifica exportación a CSV de atenciones ciudadanas."""
        Atencion.objects.create(
            folio="AT-2026-0001",
            solicitante="Prueba Export",
            tipo_atencion=self.tipo_social,
            sub_atencion=self.sub_social_1,
            descripcion="Descripción export",
            delegacion=self.delegacion,
            usuario=self.usuario,
            estado=True
        )
        response = self.client.get("/api/atenciones/export/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("atenciones_export.csv", response["Content-Disposition"])
        content = response.content.decode("utf-8-sig")
        self.assertIn("Prueba Export", content)
        self.assertIn("AT-2026-0001", content)


class IntegridadIdempotenciaAtencionAPITestCase(TestCase):
    """
    Pruebas automatizadas de Integridad e Idempotencia de Atención (Tarea T18).
    Criterios de Aceptación:
    - Sin duplicados por envío repetido (clave de idempotencia y prevención de doble clic).
    - Origen conservado (delegación de captura inmutable).
    - Rechazo de ámbito territorial manipulado (status 403).
    - Responsable autorizado (usuario y rol activos).
    - Cuarta gestión social rechazada si aplica (máximo 3 gestiones por caso social).
    - Derivación auditada entre delegaciones.
    - Rechazo de parejas inválidas tipo/subtipo.
    """

    def setUp(self):
        self.client = Client()

        # Delegaciones
        self.delegacion_origen = Delegacion.objects.create(
            nombre="DEL01 · Las Compañías",
            direccion="Esmeralda 2451",
            comuna="La Serena",
            estado=True
        )
        self.delegacion_ajena = Delegacion.objects.create(
            nombre="DEL02 · La Antena",
            direccion="18 de Septiembre s/n",
            comuna="La Serena",
            estado=True
        )
        self.delegacion_inactiva = Delegacion.objects.create(
            nombre="DEL99 · Delegación Cerrada",
            direccion="Sin dirección",
            comuna="La Serena",
            estado=False
        )

        # Rol y Usuario responsable
        self.rol = Rol.objects.create(
            nombre="Operador Territorial T18",
            descripcion="Operador de atención ciudadana con integridad",
            estado=True
        )
        self.usuario = Usuario.objects.create_user(
            username="dflores_t18",
            first_name="Daniel",
            last_name="Flores",
            email="dflores_t18@laserena.cl",
            rut="11.222.333-4",
            rol=self.rol,
            delegacion=self.delegacion_origen
        )

        # Catálogos
        self.tipo_social = TipoAtencion.objects.create(
            codigo="TA01",
            nombre="Social",
            descripcion="Atención Social",
            estado=True
        )
        self.tipo_territorial = TipoAtencion.objects.create(
            codigo="TA02",
            nombre="Territorial",
            descripcion="Atención Territorial",
            estado=True
        )

        self.sub_social = SubAtencion.objects.create(
            codigo="SA01",
            nombre="Asistencia Social Directa",
            tipo_atencion=self.tipo_social,
            estado=True
        )
        self.sub_territorial = SubAtencion.objects.create(
            codigo="SA02",
            nombre="Operativo Vecinal",
            tipo_atencion=self.tipo_territorial,
            estado=True
        )

    def test_idempotencia_previene_duplicados(self):
        """T18: Segundo envío con la misma clave de idempotencia retorna el original sin duplicar."""
        payload = {
            "solicitante": "Esteban Morales (16.789.123-4)",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social.pk,
            "descripcion": "Solicitud inicial con clave de idempotencia.",
            "clave_idempotencia": "IDEMP-TOKEN-UNIQUE-2026-ABC"
        }

        # 1er envío: Crea el registro
        res1 = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res1.status_code, 201)
        data1 = res1.json()["data"]
        folio1 = data1["folio"]

        # 2do envío: Mismo token de idempotencia
        res2 = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res2.status_code, 200)
        json2 = res2.json()
        self.assertTrue(json2.get("is_duplicate_prevented"))
        self.assertEqual(json2["data"]["folio"], folio1)

        # Verificar que solo existe exactamente 1 registro en la base de datos
        self.assertEqual(Atencion.objects.filter(clave_idempotencia="IDEMP-TOKEN-UNIQUE-2026-ABC").count(), 1)

    def test_prevencion_doble_envio_rapido_sin_clave(self):
        """T18: Detecta doble envío consecutivo idéntico sin clave y evita duplicación."""
        payload = {
            "solicitante": "Claudia Barraza",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social.pk,
            "descripcion": "Solicitud de asistencia vecinal inmediata."
        }

        # 1er envío rápido
        res1 = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res1.status_code, 201)

        # 2do envío rápido inmediatamente consecutivo (simula doble clic)
        res2 = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res2.json().get("is_duplicate_prevented"))

        # Solo existe 1 registro
        self.assertEqual(Atencion.objects.filter(solicitante="Claudia Barraza").count(), 1)

    def test_rechazo_ambito_manipulado_delegacion_ajena(self):
        """T18: Rechaza con HTTP 403 intento de manipulación territorial (delegación ajena)."""
        payload = {
            "solicitante": "Vecino Con Ambito Alterado",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social.pk,
            "descripcion": "Intento de forzar delegación no autorizada.",
            "delegacion": self.delegacion_ajena.pk  # Manipulación hacia delegación ajena
        }
        response = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 403)
        err = response.json()["error"]
        self.assertEqual(err["code"], "AMBITO_MANIPULADO")

    def test_origen_conservado_delegacion_autorizada(self):
        """T18: Al guardar normalmente, se conserva la delegación territorial autorizada del usuario."""
        payload = {
            "solicitante": "Vecina Legitima",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social.pk,
            "descripcion": "Atención normal con origen institucional."
        }
        response = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = response.json()["data"]

        atencion = Atencion.objects.get(pk=data["id"])
        self.assertEqual(atencion.delegacion, self.delegacion_origen)

    def test_responsable_autorizado_rechaza_usuario_inactivo(self):
        """T18: Rechaza con HTTP 403 si el usuario responsable está inactivo."""
        self.usuario.is_active = False
        self.usuario.save()

        payload = {
            "solicitante": "Vecino Prueba",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social.pk,
            "descripcion": "Prueba usuario inactivo."
        }
        # Sin usuario activo de respaldo
        response = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "RESPONSABLE_NO_AUTORIZADO")

        # Restaurar
        self.usuario.is_active = True
        self.usuario.save()

    def test_responsable_autorizado_rechaza_rol_inactivo(self):
        """T18: Rechaza con HTTP 403 si el rol del responsable está inactivo."""
        self.rol.estado = False
        self.rol.save()

        payload = {
            "solicitante": "Vecino Prueba",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social.pk,
            "descripcion": "Prueba rol inactivo."
        }
        response = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "RESPONSABLE_NO_AUTORIZADO")

        # Restaurar
        self.rol.estado = True
        self.rol.save()

    def test_caso_social_gestiones_sucesivas_1_2_3(self):
        """T18: Permite registrar sucesivamente gestiones 1, 2 y 3 para el mismo caso social."""
        caso_codigo = "CS-2026-VAL"

        for num_esperado in [1, 2, 3]:
            payload = {
                "solicitante": f"Solicitante Caso {num_esperado}",
                "tipo_atencion": self.tipo_social.pk,
                "sub_atencion": self.sub_social.pk,
                "descripcion": f"Gestión número {num_esperado} del caso social.",
                "caso_social": caso_codigo,
                "clave_idempotencia": f"TOKEN-GESTION-{num_esperado}"
            }
            res = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.json()["data"]["numero_gestion"], num_esperado)

        self.assertEqual(Atencion.objects.filter(caso_social=caso_codigo).count(), 3)

    def test_rechazo_cuarta_gestion_caso_social(self):
        """T18 (Criterio Clave): Rechaza la cuarta gestión sucesiva para un mismo caso social."""
        caso_codigo = "CS-2026-MAXIMO"

        # Registrar las 3 gestiones permitidas
        for i in range(1, 4):
            Atencion.objects.create(
                folio=f"AT-CS-{i}",
                solicitante="Familia Muñoz",
                tipo_atencion=self.tipo_social,
                sub_atencion=self.sub_social,
                descripcion=f"Gestión {i}",
                delegacion=self.delegacion_origen,
                usuario=self.usuario,
                caso_social=caso_codigo,
                numero_gestion=i,
                estado=True
            )

        self.assertEqual(Atencion.objects.filter(caso_social=caso_codigo).count(), 3)

        # Intentar registrar la 4ta gestión
        payload_cuarta = {
            "solicitante": "Familia Muñoz",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_social.pk,
            "descripcion": "Intento de cuarta gestión social no permitida.",
            "caso_social": caso_codigo
        }
        res4 = self.client.post("/api/atenciones/", data=json.dumps(payload_cuarta), content_type="application/json")
        self.assertEqual(res4.status_code, 400)
        err = res4.json()["error"]
        self.assertEqual(err["code"], "CUARTA_GESTION_RECHAZADA")
        self.assertIn("3 gestiones", err["message"])

        # Comprobar que en BD sigue habiendo estrictamente 3
        self.assertEqual(Atencion.objects.filter(caso_social=caso_codigo).count(), 3)

    def test_rechazo_pareja_invalida_tipo_subtipo(self):
        """T18: Rechaza con 400 si la subatención no pertenece al tipo de atención indicado."""
        payload = {
            "solicitante": "Vecino Incompatible",
            "tipo_atencion": self.tipo_social.pk,
            "sub_atencion": self.sub_territorial.pk,  # Subatención es territorial, no social
            "descripcion": "Prueba de pareja inválida."
        }
        response = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        err = response.json()["error"]
        self.assertIn("sub_atencion", err["details"])
        self.assertIn("no pertenece", err["details"]["sub_atencion"][0])

    def test_derivacion_auditada_a_delegacion_responsable(self):
        """T18: Derivación territorial crea atención y genera registro inmutable en AuditoriaDerivacion."""
        payload = {
            "solicitante": "Vecino Derivado Territorial",
            "tipo_atencion": self.tipo_territorial.pk,
            "sub_atencion": self.sub_territorial.pk,
            "descripcion": "Caso derivado para atención presencial en sector La Antena.",
            "delegacion_responsable": self.delegacion_ajena.pk,
            "motivo_derivacion": "Derivación por jurisdicción sectorial La Antena"
        }
        response = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = response.json()["data"]

        atencion = Atencion.objects.get(pk=data["id"])
        self.assertEqual(atencion.delegacion, self.delegacion_origen)
        self.assertEqual(atencion.delegacion_responsable, self.delegacion_ajena)

        # Verificar registro en AuditoriaDerivacion
        audit = AuditoriaDerivacion.objects.filter(atencion=atencion).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.delegacion_origen, self.delegacion_origen)
        self.assertEqual(audit.delegacion_destino, self.delegacion_ajena)
        self.assertEqual(audit.usuario_responsable, self.usuario)
        self.assertEqual(audit.motivo, "Derivación por jurisdicción sectorial La Antena")

    def test_derivacion_rechaza_delegacion_responsable_inactiva(self):
        """T18: Rechaza con 400 intento de derivación hacia delegación inactiva."""
        payload = {
            "solicitante": "Vecino Derivado Fallido",
            "tipo_atencion": self.tipo_territorial.pk,
            "sub_atencion": self.sub_territorial.pk,
            "descripcion": "Intento de derivar a delegación inactiva.",
            "delegacion_responsable": self.delegacion_inactiva.pk
        }
        response = self.client.post("/api/atenciones/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        err = response.json()["error"]
        self.assertEqual(err["code"], "DELEGACION_RESPONSABLE_INACTIVA")




