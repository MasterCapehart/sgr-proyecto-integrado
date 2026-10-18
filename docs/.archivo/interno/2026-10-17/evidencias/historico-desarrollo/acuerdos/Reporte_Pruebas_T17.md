# Reporte de Pruebas y Validación: Conectar Registro de Atención Ciudadana (Tarea T17)

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Delegación Municipal Las Compañías
**Responsable:** Daniel Flores
**Revisor Asignado:** Daniel Angel
**Fecha:** 12 de Octubre de 2026
**Rama:** `feat/atencion-real`
**Estado:** ✅ Aprobado y Verificado (43/43 Pruebas Automatizadas Pasadas)

---

## 1. Resumen de la Tarea T17
* **Objetivo:** Conectar de extremo a extremo el formulario de registro de atención ciudadana (Pantalla M-20: `frontend/pages/ingreso-atencion.html`) con la API REST de Django y la base de datos MySQL `sgr_prueba`.
* **Criterios de Aceptación Cumplidos:**
  1. **Registro Persiste:** La atención se guarda de forma real y atómica en la tabla `core_atencion` de MySQL `sgr_prueba`.
  2. **ID y Folio Reales:** El servidor genera un folio oficial correlativo e incremental (`AT-{año}-{correlativo:04d}`, ej. `AT-2026-0001`) y retorna el ID numérico primario de base de datos.
  3. **Catálogos Activos:** Carga dinámica exclusiva de tipos de atención y subatenciones activas (`estado=True`). Rechazo en servidor si se intenta registrar con un catálogo inactivo.
  4. **Compatibilidad Estricta Tipo/Subtipo:** Verificación en el servidor de que la subatención seleccionada pertenezca obligatoriamente al tipo de atención indicado.
  5. **Inmutabilidad del Contexto Institucional:** Autor (`usuario`), delegación territorial de captura (`delegacion`) y fecha/hora (`fecha_registro`) son fijados por el servidor según la sesión activa y no pueden ser alterados ni suplantados por el cliente.
  6. **Cancelar no guarda:** Cancelar o limpiar el formulario en el cliente descarta las modificaciones sin emitir solicitudes de persistencia ni alterar la base de datos.

---

## 2. Componentes Implementados

### 2.1. Modelo y Migración de Base de Datos ([`backend/core/models.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/models.py))
1. **`Atencion(models.Model)`:**
   * `folio`: CharField(max_length=64, unique=True, db_index=True).
   * `solicitante`: CharField(max_length=200).
   * `tipo_atencion`: ForeignKey(`TipoAtencion`, on_delete=models.PROTECT, related_name='atenciones').
   * `sub_atencion`: ForeignKey(`SubAtencion`, on_delete=models.PROTECT, related_name='atenciones').
   * `descripcion`: TextField().
   * `delegacion`: ForeignKey(`Delegacion`, on_delete=models.PROTECT, related_name='atenciones_origen').
   * `delegacion_responsable`: ForeignKey(`Delegacion`, on_delete=models.PROTECT, null=True, blank=True).
   * `usuario`: ForeignKey(`Usuario`, on_delete=models.PROTECT, related_name='atenciones_creadas').
   * `fecha_registro`: DateTimeField(auto_now_add=True).
   * `caso_social`: CharField(max_length=50, null=True, blank=True).
   * `numero_gestion`: PositiveSmallIntegerField(default=1, null=True, blank=True).
   * `clave_idempotencia`: CharField(max_length=64, unique=True, null=True, blank=True).
   * `estado`: BooleanField(default=True).
2. **Migración:** `0005_atencion.py` creada y aplicada exitosamente en MySQL `sgr_prueba`.
3. **Registro en Django Admin:** Registrado en [`backend/core/admin.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/admin.py).

### 2.2. Backend API ([`backend/core/views.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py) y [`urls.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/urls.py))
1. **`AtencionContextoView`:**
   * Endpoint `GET /api/atenciones/contexto/`.
   * Provee los datos de identidad municipal: funcionario activo, delegación activa y fecha del servidor.
2. **`AtencionCRUDView`:**
   * `POST /api/atenciones/`: Valida obligatorios, catálogos activos, compatibilidad jerárquica y guarda atómicamente con folio `AT-2026-XXXX`. Retorna HTTP 201 Created.
   * `GET /api/atenciones/`: Listado paginado con búsqueda por solicitante, folio o descripción.
   * `GET /api/atenciones/<id>/`: Consulta y recuperación del registro persistido.
   * `GET /api/atenciones/export/`: Exportación a CSV oficial para auditoría institucional.
3. **`SubAtencionCRUDView`:**
   * Soporte agregado para filtrar subatenciones dependientes por tipo padre vía parámetro `?tipo_atencion=<id>&estado=activos`.

### 2.3. Frontend ([`frontend/assets/js/modules/ingreso-atencion.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/ingreso-atencion.js))
* Consulta dinámica del contexto institucional (`loadServerContext`) para poblar los campos de solo lectura (`#delegacion-contexto`, `#responsable-nombre`).
* Consulta dinámica de `/api/tipos-atencion/?estado=activos` al inicializar.
* Listener en `#tipo-atencion` que consulta en vivo `/api/subatenciones/?tipo_atencion={id}&estado=activos` y llena `#subtipo-atencion`.
* Muestra condicionalmente la sección `#seccion-caso-social` únicamente si el tipo seleccionado es Social.
* Botón "Cancelar" con confirmación de SweetAlert2 que descarta datos sin enviar nada al backend.
* Envío de formulario con prevención de doble clic y confirmación con folio oficial e ID real en caso de éxito.

---

## 3. Matriz de Pruebas Automatizadas (`core.tests`)

Comando ejecutado: `./venv/bin/python manage.py test core`

| Caso de Prueba | Tipo | Descripción | Resultado |
|---|:---:|---|:---:|
| `test_atencion_contexto_servidor` | **T17** | **Consulta de contexto institucional de funcionario y delegación** | ✅ PASS |
| `test_atencion_create_success_with_real_folio` | **T17** | **Creación exitosa: genera folio real correlativo `AT-YYYY-XXXX` y persiste en MySQL** | ✅ PASS |
| `test_atencion_persistencia_y_recarga` | **T17** | **Consulta por ID recupera correctamente todos los atributos guardados** | ✅ PASS |
| `test_atencion_rejected_incompatible_subtipo` | **T17** | **Rechaza (400) si la subatención no pertenece al tipo de atención indicado** | ✅ PASS |
| `test_atencion_rejected_inactive_tipo` | **T17** | **Rechaza (400) si el catálogo tipo de atención está inactivo** | ✅ PASS |
| `test_atencion_rejected_inactive_subtipo` | **T17** | **Rechaza (400) si la subatención solicitada está inactiva** | ✅ PASS |
| `test_atencion_rejected_missing_required_fields` | **T17** | **Rechaza (400) si faltan solicitante o descripción requeridos** | ✅ PASS |
| `test_atencion_server_context_immutable` | **T17** | **Autor y delegación inmutables: ignora intentos de manipulación desde el cliente** | ✅ PASS |
| `test_atencion_cancel_does_not_save` | **T17** | **Cancelar la operación en el cliente no genera registros en base de datos** | ✅ PASS |
| `test_atencion_export_csv` | **T17** | **Generación y descarga de archivo CSV con folios y solicitantes** | ✅ PASS |
| *(33 Pruebas previas T04, T14, T15, T16)* | **Regresión Base** | **Verificación continua de auth, roles, tipos, subatenciones e ítems/metas** | ✅ PASS |

**Total de Pruebas Ejecutadas:** 43
**Tiempo de Ejecución:** ~0.15 segundos
**Tasa de Éxito:** 100% (43/43)
