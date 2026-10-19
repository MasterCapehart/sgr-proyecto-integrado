# Reporte de Pruebas y Validación: CRUD Subatenciones (Tarea T15)

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Delegación Municipal Las Compañías  
**Responsable:** Daniel Flores  
**Revisor Asignado:** Daniel Angel  
**Fecha:** 12 de Octubre de 2026  
**Rama:** `feat/subatenciones-real`  
**Estado:** ✅ Aprobado y Verificado (25/25 Pruebas Automatizadas Pasadas)

---

## 1. Resumen de la Tarea T15
* **Objetivo:** Completar el CRUD real de Subatenciones (catálogo hijo dependiente de Tipos de Atención), conectando la interfaz de usuario con la API REST y la base de datos MySQL `sgr_prueba`.
* **Criterios de Aceptación:**
  1. CRUD real de extremo a extremo (Frontend $\leftrightarrow$ API REST $\leftrightarrow$ MySQL).
  2. Asociación obligatoria y correcta a un catálogo padre (`TipoAtencion`).
  3. Validación de servidor: solo se permite asociar o actualizar subatenciones si el Tipo de Atención padre está **activo**.
  4. Control de duplicados en código y en nombre (no se permite el mismo nombre bajo el mismo padre).
  5. Listado dinámico con búsqueda por código, nombre o tipo padre, y exportación común descargable.

---

## 2. Componentes Implementados

### 2.1. Backend (`backend/core/`)
1. **`SubAtencionCRUDView` ([`backend/core/views.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py)):**
   * Consulta optimizada con `select_related("tipo_atencion")`.
   * Serialización enriquecida con `tipo_padre_display` (`"TA01 · Social"`).
   * `validate_payload`:
     * Valida existencia y estado activo del catálogo padre (`PARENT_INACTIVE` si está inactivo).
     * Rechazo de código duplicado.
     * Rechazo de nombre duplicado bajo el mismo padre.
   * `export`: Genera `subatenciones_export.csv` con columna del tipo padre.
2. **Rutas REST ([`backend/core/urls.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/urls.py)):**
   * `/api/subatenciones/` (Listado y creación).
   * `/api/subatenciones/<id>/` (Detalle y edición).
   * `/api/subatenciones/<id>/toggle-estado/` (Alternar activo / inactivo).
   * `/api/subatenciones/export/` (Descarga directa a Excel/CSV).

### 2.2. Frontend ([`frontend/assets/js/modules/mantenedor-comun.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/mantenedor-comun.js))
* **Selector Dinámico del Padre:** Al pulsar "+ Nueva subatención" o "Editar", consulta automáticamente `/api/tipos-atencion/?estado=activos` y llena las opciones de `<select id="campo-padre">` con los tipos disponibles.
* **Tabla en Vivo:** Muestra la columna "Tipo de Atención (Padre)" con el badge de estado correspondiente.
* **Gestión de Errores con SweetAlert2:** Muestra las alertas de rechazo si se intenta seleccionar un padre no válido o un código duplicado.

---

## 3. Matriz de Pruebas Automatizadas (`core.tests`)

Comando ejecutado: `./venv/bin/python manage.py test core`

| Caso de Prueba | Tipo | Descripción | Resultado |
|---|:---:|---|:---:|
| `test_subatencion_list_with_parent_display` | **T15** | **Listado incluye datos del tipo padre (`tipo_padre_display`)** | ✅ PASS |
| `test_subatencion_search_by_parent_name` | **T15** | **Búsqueda por nombre del catálogo padre** | ✅ PASS |
| `test_subatencion_create_success_with_active_parent` | **T15** | **Creación exitosa asociando padre activo** | ✅ PASS |
| `test_subatencion_create_inactive_parent_rejected` | **T15** | **Rechaza asociación si el padre está inactivo** | ✅ PASS |
| `test_subatencion_create_missing_parent_rejected` | **T15** | **Rechaza creación sin indicar catálogo padre** | ✅ PASS |
| `test_subatencion_duplicate_codigo_rejected` | **T15** | **Rechaza código de subatención duplicado** | ✅ PASS |
| `test_subatencion_duplicate_nombre_under_same_parent_rejected` | **T15** | **Rechaza nombre duplicado bajo el mismo padre** | ✅ PASS |
| `test_subatencion_toggle_estado` | **T15** | **Alterna estado activo/inactivo de la subatención** | ✅ PASS |
| `test_subatencion_export_csv` | **T15** | **Exporta CSV con columna de Tipo de Atención Padre** | ✅ PASS |
| *(Otras 16 pruebas de Base y T14)* | Regresión | Modelos base, paginación, filtros y TipoAtencion | ✅ PASS |

**Resultado acumulado:** 25 pruebas ejecutadas en 0.087s — **100% OK**.
