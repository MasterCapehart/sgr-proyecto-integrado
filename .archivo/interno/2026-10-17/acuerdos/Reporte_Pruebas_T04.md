# Reporte de Ejecución y Pruebas del Patrón Común de CRUD (Tarea T04)

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Delegación Municipal Las Compañías  
**Responsable:** Daniel Flores  
**Revisor Asignado:** Daniel Angel  
**Fecha:** 12 de Octubre de 2026  
**Rama:** `backend/patron-crud`  
**Estado:** ✅ Superado Exitosamente (11/11 Pruebas Aprobadas)

---

## 1. Resumen de la Tarea T04
* **Objetivo:** Definir el contrato de API, entradas, salidas, errores, filtros y paginación; proveer un ejemplo real conectado reutilizable en Django (`TipoAtencion` y `Delegacion`).
* **Criterio de Aceptación:** Contrato documentado y ejemplo real funcional; Matías puede aplicar el patrón a Delegaciones con mínimo esfuerzo.

---

## 2. Entorno y Ejecución de Pruebas
* **Comando:** `./venv/bin/python manage.py test core`
* **Motor:** MySQL 8.0 (Base de pruebas temporal administrada por Django)
* **Tiempo de ejecución:** 0.039 segundos
* **Total de pruebas:** 11 pruebas unitarias y de integración

---

## 3. Matriz de Pruebas Ejecutadas

| # | Caso de Prueba | Método / Escenario | Resultado Obtenido | Estado |
|:---:|---|---|---|:---:|
| 1 | `test_list_pagination_default` | `GET /api/tipos-atencion/` con 15 registros | Retorna 10 registros, `page=1`, `total_pages=2`, `count=15` | ✅ PASS |
| 2 | `test_list_filter_by_estado` | `?estado=activos` y `?estado=inactivos` | Retorna exactamente 8 activos y 7 inactivos respectivamente | ✅ PASS |
| 3 | `test_list_search_query` | `?search=TA-05` | Retorna exactamente el registro `TA-05` mediante coincidencia parcial | ✅ PASS |
| 4 | `test_retrieve_detail_success` | `GET /api/tipos-atencion/<id>/` | Retorna código `200 OK` con el sobre uniforme `{"success": true, "data": ...}` | ✅ PASS |
| 5 | `test_retrieve_not_found` | `GET /api/tipos-atencion/99999/` | Retorna código `404 Not Found` con `error.code="NOT_FOUND"` | ✅ PASS |
| 6 | `test_create_success` | `POST /api/tipos-atencion/` con JSON | Retorna código `201 Created`, persiste en BD y devuelve ID asignado | ✅ PASS |
| 7 | `test_create_validation_error` | `POST` sin campos obligatorios | Retorna código `400 Bad Request` con mapa de errores en `error.details` | ✅ PASS |
| 8 | `test_update_patch_success` | `PATCH /api/tipos-atencion/<id>/` | Retorna `200 OK`, actualiza solo el campo enviado y persiste en BD | ✅ PASS |
| 9 | `test_soft_delete` | `DELETE /api/tipos-atencion/<id>/` | Retorna `200 OK`, preserva el registro y cambia `estado=False` | ✅ PASS |
| 10 | `test_toggle_estado` | `POST /api/tipos-atencion/<id>/toggle-estado/` | Alterna con éxito de True a False y de vuelta a True | ✅ PASS |
| 11 | `test_reusability_delegacion_crud` | Aplicación del patrón a `Delegacion` | Valida que `DelegacionCRUDView` funciona idénticamente (Caso Matías T13) | ✅ PASS |

---

## 4. Evidencia de Ejecución en Consola
```text
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...........
----------------------------------------------------------------------
Ran 11 tests in 0.039s

OK
Destroying test database for alias 'default'...
```

---

## 5. Archivos Implementados en la Entrega
1. [`backend/core/api.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/api.py): Clase base reusable `BaseCRUDView` y helpers de respuesta estándar (`api_success`, `api_error`).
2. [`backend/core/views.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py): Implementación del ejemplo real conectado `TipoAtencionCRUDView` y vista modelo `DelegacionCRUDView`.
3. [`backend/core/urls.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/urls.py): Enrutamiento REST bajo el prefijo `/api/`.
4. [`backend/config/urls.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/config/urls.py): Registro central de la API en el proyecto Django.
5. [`backend/core/tests.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/tests.py): Suite de pruebas automatizadas (11 casos).
6. [`docs/acuerdos/Contrato_API_Patron_CRUD.md`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/docs/acuerdos/Contrato_API_Patron_CRUD.md): Contrato formal documentado.
