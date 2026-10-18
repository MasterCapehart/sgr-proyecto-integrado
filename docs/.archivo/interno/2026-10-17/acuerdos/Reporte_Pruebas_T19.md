# Reporte de Pruebas y Validación: Integrar Cabecera y Cambio de Delegación (Tarea T19)

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Delegación Municipal Las Compañías  
**Responsable:** Daniel Flores  
**Revisor Asignado:** Daniel Angel (`danielangelrojas07-aaa`)  
**Fecha:** 12 de Octubre de 2026  
**Rama:** `feat/cabecera-contexto`  
**Estado:** ✅ Aprobado y Verificado (61/61 Pruebas Automatizadas Pasadas)

---

## 1. Resumen de la Tarea T19
* **Objetivo:** Conectar el contexto institucional permanente en la cabecera del sistema para todas las vistas privadas (identidad del funcionario, rol asignado y delegación territorial activa). Permitir el cambio interactivo de ámbito territorial entre delegaciones autorizadas y activas, advirtiendo al usuario si existen datos no guardados y propagando el cambio reactivamente a formularios, listados y exportaciones a Excel.
* **Criterios de Aceptación Cumplidos:**
  1. **Contexto Permanente en Vistas Privadas:**
     * Integración de datos reales en la cabecera: nombre completo, RUT, rol municipal asignado y selector de delegación activa.
     * Persistencia bidireccional mediante sesión del servidor (`request.session['delegacion_activa_id']`) y caché local en el navegador (`sessionStorage`) para eliminar parpadeos de interfaz entre navegaciones.
  2. **Selector de Ámbitos Autorizados:**
     * Selector interactivo `<select id="session-delegation-select">` en la cabecera que lista exclusivamente las delegaciones municipales existentes con estado activo (`estado=True`).
  3. **Advertencia de Datos sin Guardar (Unsaved Changes):**
     * Función `hasUnsavedChanges()` que detecta datos ingresados en el formulario de atención ciudadana (`#form-atencion`) o modales CRUD abiertos (`#modal-editor`).
     * En caso de haber cambios pendientes, SweetAlert2 despliega un diálogo de confirmación antes de autorizar el cambio territorial. Si el usuario cancela, el selector revierte inmediatamente a la delegación previa sin alterar el estado.
  4. **Propagación y Actualización de Vistas:**
     * Emisión del evento global `sgr:delegacion-cambiada` tras cada cambio exitoso en el backend.
     * El formulario de registro de atención (`ingreso-atencion.js`) actualiza su campo de delegación de origen en tiempo real.
     * Los mantenedores y listados (`mantenedor-comun.js`) recargan sus datos automáticamente desde la API.
  5. **Impacto en Formularios, Listados y Excel:**
     * Al registrar nuevas atenciones ciudadanas, el servidor fija como `delegacion_origen` la delegación territorial activa de la sesión.
     * Los endpoints de consulta y exportación a Excel/CSV de atenciones (`/api/atenciones/?solo_activa=1` y `/api/atenciones/export/?solo_activa=1`) filtran fielmente por la delegación activa.

---

## 2. Componentes Implementados

### 2.1. Backend API y Sesión ([`backend/core/views.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py))
1. **Endpoint `GET /api/contexto/` (`ContextoView`):**
   * Retorna información del usuario autenticado (nombre, rut, rol, display), delegación territorial activa actual, listado de delegaciones activas autorizadas en el sistema y marcas temporales del servidor.
   * Inicializa `request.session['delegacion_activa_id']` si no estaba previamente definida.
2. **Endpoint `POST /api/contexto/cambiar-delegacion/` (`CambiarDelegacionView`):**
   * Recibe `delegacion_id` y valida existencia y estado activo.
   * Rechaza con HTTP 400 (`DELEGACION_REQUIRED`) si falta el parámetro.
   * Rechaza con HTTP 404 (`DELEGACION_NOT_FOUND`) si la delegación no existe.
   * Rechaza con HTTP 400 (`DELEGACION_INACTIVA`) si la delegación se encuentra inactiva.
   * Actualiza `request.session['delegacion_activa_id']` y el atributo `user.delegacion` del funcionario autenticado.
3. **Integración con Atención Ciudadana:**
   * `AtencionContextoView` prioriza la delegación activa guardada en la sesión.
   * `AtencionCRUDView.post` resuelve `delegacion_origen` desde la sesión institucional activa.
   * `AtencionCRUDView.filter_queryset` añade soporte para filtrar por `?solo_activa=1` o `?delegacion=<id>`.
   * `AtencionCRUDView.export` respeta dicho filtrado para generar planillas Excel/CSV acotadas al ámbito activo.

### 2.2. Enrutador y CORS ([`backend/core/urls.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/urls.py), [`backend/config/cors_middleware.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/config/cors_middleware.py))
* Rutas registradas: `contexto/` y `contexto/cambiar-delegacion/`.
* Encabezados CORS actualizados para habilitar cabeceras institucionales.

### 2.3. Frontend ([`frontend/assets/js/components/layout.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/components/layout.js), [`frontend/assets/css/styles.css`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/css/styles.css))
* Inyección dinámica de `<select id="session-delegation-select" class="delegation-select">` en la cabecera privada.
* Sistema de caché con `sessionStorage` para mantener la experiencia de usuario fluida y sin saltos visuales.
* Manejador de eventos con detección de cambios no guardados (`hasUnsavedChanges`) y confirmación SweetAlert2.
* Disparo de evento `sgr:delegacion-cambiada`.
* Escucha reactiva en [`ingreso-atencion.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/ingreso-atencion.js) y [`mantenedor-comun.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/mantenedor-comun.js).

---

## 3. Matriz de Pruebas Automatizadas (`core.tests`)

Comando ejecutado: `./venv/bin/python manage.py test core`

| Caso de Prueba | Tipo | Descripción | Resultado |
|---|:---:|---|:---:|
| `test_contexto_global_get_exitoso` | **T19** | **GET /api/contexto/ retorna usuario, rol, delegación activa y delegaciones autorizadas** | ✅ PASS |
| `test_cambiar_delegacion_exitoso_y_persistencia_sesion` | **T19** | **POST /api/contexto/cambiar-delegacion/ actualiza sesión y persiste entre solicitudes** | ✅ PASS |
| `test_cambiar_delegacion_rechaza_inactiva` | **T19** | **Rechaza con HTTP 400 intento de cambio hacia delegación inactiva** | ✅ PASS |
| `test_cambiar_delegacion_rechaza_inexistente` | **T19** | **Rechaza con HTTP 404 intento de cambio a delegación no existente** | ✅ PASS |
| `test_cambiar_delegacion_requiere_id` | **T19** | **Rechaza con HTTP 400 si delegacion_id no se proporciona en el cuerpo** | ✅ PASS |
| `test_cambio_delegacion_afecta_creacion_atencion` | **T19** | **Nuevas atenciones adoptan el ámbito territorial activo fijado en la sesión** | ✅ PASS |
| `test_filtro_y_export_por_delegacion_activa` | **T19** | **Listado y exportación CSV/Excel filtran según el ámbito territorial activo** | ✅ PASS |
| *(54 Pruebas previas T04, T14, T15, T16, T17, T18)* | **Regresión Base** | **Verificación continua de CRUDs, autenticación, integridad e idempotencia** | ✅ PASS |

**Total de Pruebas Ejecutadas:** 61  
**Tiempo de Ejecución:** ~0.93 segundos  
**Tasa de Éxito:** 100% (61/61)
