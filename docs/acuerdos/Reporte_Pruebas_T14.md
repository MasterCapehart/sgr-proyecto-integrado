# Reporte de Pruebas y Validación: CRUD Tipo de Atención (Tarea T14)

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Delegación Municipal Las Compañías  
**Responsable:** Daniel Flores  
**Revisor Asignado:** Daniel Angel  
**Fecha:** 12 de Octubre de 2026  
**Rama:** `feat/tipos-atencion-real`  
**Estado:** ✅ Aprobado y Verificado (16/16 Pruebas Automatizadas Pasadas)

---

## 1. Resumen de la Tarea T14
* **Objetivo:** Completar el CRUD real de Tipos de Atención (catálogo padre) conectando la interfaz de usuario con la API REST y la base de datos MySQL `sgr_prueba`.
* **Criterios de Aceptación:**
  1. CRUD real de extremo a extremo (Frontend $\leftrightarrow$ API REST $\leftrightarrow$ MySQL).
  2. Control estricto de duplicados en código y nombre.
  3. Rechazo de cambios inválidos por referencias (no se permite desactivar ni eliminar un Tipo de Atención si posee subatenciones activas vinculadas).
  4. Listado con filtros de estado y búsqueda dinámica.
  5. Exportación común descargable en formato compatible con Excel.

---

## 2. Componentes Implementados

### 2.1. Backend (`backend/core/`)
1. **Modelo `SubAtencion` ([`backend/core/models.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/models.py)):**
   * Vinculado a `TipoAtencion` mediante `ForeignKey(TipoAtencion, on_delete=models.PROTECT)`.
   * Migración generada y ejecutada: `0002_subatencion.py`.
2. **Validaciones en `TipoAtencionCRUDView` ([`backend/core/views.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py)):**
   * `validate_payload`: Impide códigos o nombres duplicados (`400 Bad Request`).
   * `delete` y `toggle_estado`: Evalúan `subatenciones.filter(estado=True).exists()` y bloquean la desactivación con código `HAS_ACTIVE_DEPENDENCIES` si hay hijos activos.
   * `export`: Genera archivo CSV con codificación UTF-8 con BOM para apertura inmediata en Excel.
3. **CORS Middleware ([`backend/config/cors_middleware.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/config/cors_middleware.py)):**
   * Habilita peticiones AJAX/fetch entre el frontend local y la API Django sin dependencias pesadas.

### 2.2. Frontend ([`frontend/assets/js/modules/mantenedor-comun.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/mantenedor-comun.js))
* **Carga en vivo:** Consume `GET /api/tipos-atencion/?search=...&estado=...` y puebla la tabla en tiempo real.
* **Creación y Edición:** Envía peticiones `POST` / `PATCH` con SweetAlert2 mostrando mensajes reales del servidor o errores de validación.
* **Desactivación / Toggle:** Invoca `POST /api/tipos-atencion/<id>/toggle-estado/`. Si el backend rechaza la acción por referencias activas, SweetAlert2 advierte al usuario.
* **Exportar a Excel:** Dispara la descarga directa de `tiposatencion_export.csv`.

---

## 3. Matriz de Pruebas Automatizadas (`core.tests`)

Comando ejecutado: `./venv/bin/python manage.py test core`

| Caso de Prueba | Tipo | Descripción | Resultado |
|---|:---:|---|:---:|
| `test_list_pagination_default` | Integración | Paginación por defecto y cálculo de páginas | ✅ PASS |
| `test_list_filter_by_estado` | Integración | Filtro `?estado=activos` e `inactivos` | ✅ PASS |
| `test_list_search_query` | Integración | Búsqueda por coincidencia parcial | ✅ PASS |
| `test_retrieve_detail_success` | Integración | Detalle individual de registro | ✅ PASS |
| `test_retrieve_not_found` | Integración | Error 404 estructurado ante ID inexistente | ✅ PASS |
| `test_create_success` | Integración | Creación de registro con persistencia | ✅ PASS |
| `test_create_validation_error_missing_field` | Validación | Rechazo ante campos obligatorios omitidos | ✅ PASS |
| `test_create_duplicate_codigo_rejected` | **T14** | **Rechazo de código duplicado** | ✅ PASS |
| `test_create_duplicate_nombre_rejected` | **T14** | **Rechazo de nombre duplicado** | ✅ PASS |
| `test_reject_deactivation_with_active_subatenciones` | **T14** | **Bloqueo de desactivación con referencias activas** | ✅ PASS |
| `test_allow_deactivation_when_subatenciones_inactive` | **T14** | **Permite desactivar cuando hijos están inactivos** | ✅ PASS |
| `test_export_tipos_atencion_csv` | **T14** | **Descarga de CSV para Excel con encabezados correctos** | ✅ PASS |
| `test_update_patch_success` | Integración | Actualización parcial mediante PATCH | ✅ PASS |
| `test_soft_delete` | Integración | Desactivación lógica conservando fila | ✅ PASS |
| `test_toggle_estado` | Integración | Alternancia de estado activo / inactivo | ✅ PASS |
| `test_reusability_delegacion_crud` | Reusabilidad | Aplicación del patrón común en Delegaciones | ✅ PASS |

**Resultado final:** 16 pruebas ejecutadas en 0.057s — **100% OK**.
