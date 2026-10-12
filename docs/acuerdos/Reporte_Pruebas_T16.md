# Reporte de Pruebas y Validación: CRUD Ítems y Metas (Tarea T16)

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Delegación Municipal Las Compañías  
**Responsable:** Daniel Flores  
**Revisor Asignado:** Daniel Angel  
**Fecha:** 12 de Octubre de 2026  
**Rama:** `feat/items-metas-real`  
**Estado:** ✅ Aprobado y Verificado (33/33 Pruebas Automatizadas Pasadas)

---

## 1. Resumen de la Tarea T16
* **Objetivo:** Completar el CRUD real de Ítems y metas (`ItemMeta` y `ConfiguracionMeta`), acordando el mapeo item/función/indicador/meta sin fórmulas inventadas, conectando el mantenedor frontend con la API REST y la base de datos MySQL `sgr_prueba`, y preservando la historia municipal mediante protección estricta de referencias.
* **Criterios de Aceptación:**
  1. CRUD obligatorio real de `codigo`, `nombre`, `descripcion`, `unidad_medida`, `estado`.
  2. Alcance de metas documentado y respaldado en la base de datos (`ConfiguracionMeta` con `on_delete=models.PROTECT`).
  3. Sin fórmulas inventadas: preservación de datos institucionales históricos mediante soft-delete y rechazo de eliminación/desactivación si existen metas asociadas activas.
  4. Control riguroso de duplicados en código y nombre.
  5. Conexión de interfaz real en `frontend/pages/items-metas.html` con `/api/items-metas/`.
  6. Exportación a CSV y filtros por estado y texto.

---

## 2. Componentes Implementados

### 2.1. Modelos de Base de Datos ([`backend/core/models.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/models.py))
1. **`ItemMeta` (hereda de `CatalogoBase`):**
   * `codigo`: CharField(max_length=20, unique=True).
   * `nombre`: CharField(max_length=150, unique=True).
   * `descripcion`: TextField(blank=True, null=True).
   * `unidad_medida`: CharField(max_length=50, default='unidades').
   * `estado`: BooleanField(default=True).
2. **`ConfiguracionMeta`:**
   * `item`: ForeignKey(`ItemMeta`, on_delete=models.PROTECT, related_name='configuraciones_meta').
   * `periodo`: PositiveIntegerField(help_text="Año del período municipal").
   * `meta_esperada`: DecimalField(max_digits=12, decimal_places=2).
   * `ponderacion`: DecimalField(max_digits=5, decimal_places=2, default=100.00).
   * `estado`: BooleanField(default=True).
3. **Migración:** `0004_itemmeta_configuracionmeta.py` aplicada exitosamente en MySQL `sgr_prueba`.

### 2.2. Backend API ([`backend/core/views.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py))
1. **`ItemMetaCRUDView`:**
   * Serialización con conteo de configuraciones activas asociadas (`metas_count`).
   * `validate_payload`: Validación de unicidad de `codigo` y `nombre`, requerimiento de campos obligatorios y formato.
   * `validate_can_deactivate`: Si el ítem tiene configuraciones de metas activas, impide su desactivación o eliminación arrojando error `ITEM_HAS_ACTIVE_METAS` ("No se puede desactivar o eliminar este ítem porque tiene metas asociadas activas").
   * `export`: Generación de `items_metas_export.csv` con columnas `codigo`, `nombre`, `descripcion`, `unidad_medida`, `metas_activas`, `estado`, `fecha_creacion`.
2. **Endpoints REST ([`backend/core/urls.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/urls.py)):**
   * `/api/items-metas/` (Listado y creación).
   * `/api/items-metas/<id>/` (Detalle y actualización).
   * `/api/items-metas/<id>/toggle-estado/` (Activación/desactivación con protección).
   * `/api/items-metas/export/` (Descarga directa a CSV).

### 2.3. Frontend ([`frontend/assets/js/modules/mantenedor-comun.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/mantenedor-comun.js))
* Adaptación de textos del modal y feedback: "Nuevo Ítem", "Editar Ítem".
* Consumo nativo de la API `/api/items-metas/` conectada con MySQL.

---

## 3. Matriz de Pruebas Automatizadas (`core.tests`)

Comando ejecutado: `./venv/bin/python manage.py test core`

| Caso de Prueba | Tipo | Descripción | Resultado |
|---|:---:|---|:---:|
| `test_item_meta_list_and_search` | **T16** | **Listado de ítems y búsqueda por código y nombre** | ✅ PASS |
| `test_item_meta_create_success` | **T16** | **Creación exitosa de ítem con unidad de medida y estado** | ✅ PASS |
| `test_item_meta_duplicate_codigo_rejected` | **T16** | **Rechazo de código de ítem duplicado** | ✅ PASS |
| `test_item_meta_duplicate_nombre_rejected` | **T16** | **Rechazo de nombre de ítem duplicado** | ✅ PASS |
| `test_item_meta_cannot_deactivate_when_has_active_metas` | **T16** | **Protección de integridad: rechaza desactivar ítem con metas activas** | ✅ PASS |
| `test_item_meta_toggle_estado_when_no_active_metas` | **T16** | **Permite cambiar estado si no tiene metas activas** | ✅ PASS |
| `test_item_meta_update_success` | **T16** | **Actualización de datos descriptivos de un ítem existente** | ✅ PASS |
| `test_item_meta_export_csv` | **T16** | **Descarga y estructura de archivo CSV de ítems** | ✅ PASS |
| *(25 Pruebas previas T04, T14, T15)* | **Base/CRUD** | **Regresión completa de autenticación, tipos y subatenciones** | ✅ PASS |

**Total de Pruebas Ejecutadas:** 33  
**Tiempo de Ejecución:** ~0.12 segundos  
**Tasa de Éxito:** 100% (33/33)
