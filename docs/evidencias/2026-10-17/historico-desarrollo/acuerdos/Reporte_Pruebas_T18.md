# Reporte de Pruebas y Validación: Integridad e Idempotencia de Atención (Tarea T18)

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Delegación Municipal Las Compañías
**Responsable:** Daniel Flores
**Revisor Asignado:** Daniel Angel
**Fecha:** 12 de Octubre de 2026
**Rama:** `fix/integridad-atencion`
**Estado:** ✅ Aprobado y Verificado (54/54 Pruebas Automatizadas Pasadas)

---

## 1. Resumen de la Tarea T18
* **Objetivo:** Implementar y garantizar los mecanismos de seguridad, integridad transaccional, idempotencia ante envíos repetidos, auditoría de derivaciones territoriales y la regla institucional de máximo 3 gestiones por Caso Social en el registro de atención ciudadana (M-20).
* **Criterios de Aceptación Cumplidos:**
  1. **Sin duplicados por envío repetido:** Mecanismo doble de idempotencia:
     * Soporte de tokens de idempotencia (`clave_idempotencia` en payload y cabecera `X-Idempotency-Key`). El reenvío con la misma clave devuelve el registro original con status 200 y `is_duplicate_prevented: true`.
     * Detección de doble clic rápido consecutivo para solicitudes idénticas en una ventana corta.
  2. **Origen Conservado:** La delegación de origen de la atención queda estrictamente fijada a la delegación territorial autorizada del funcionario.
  3. **Rechazo de Ámbito Manipulado:** Si un cliente intenta enviar una delegación ajena a su ámbito autorizado, el servidor rechaza la solicitud con HTTP 403 (`AMBITO_MANIPULADO`).
  4. **Responsable Autorizado:** Verificación de que el usuario funcionario y su rol asignado estén activos en el sistema municipal (`RESPONSABLE_NO_AUTORIZADO` con status 403 si están inactivos).
  5. **Rechazo Estricto de la Cuarta Gestión Social:** Un caso social permite hasta 3 gestiones sucesivas (`numero_gestion` del 1 al 3). Un cuarto intento de registro bajo el mismo código de caso social es rechazado con HTTP 400 (`CUARTA_GESTION_RECHAZADA`).
  6. **Derivación Territorial Auditada:** Cuando la delegación responsable difiere de la delegación de origen, la atención se registra y se genera un registro inmutable en `AuditoriaDerivacion` con trazabilidad completa (origen, destino, usuario, motivo y fecha).
  7. **Rechazo de Pareja Inválida:** Verificación de compatibilidad jerárquica estricta entre Tipo de Atención y Subatención.

---

## 2. Componentes Implementados

### 2.1. Modelos de Base de Datos ([`backend/core/models.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/models.py))
1. **Método `clean()` en `Atencion`:**
   * Valida compatibilidad tipo/subtipo.
   * Valida restricción `numero_gestion BETWEEN 1 AND 3` para casos sociales.
2. **Modelo `AuditoriaDerivacion`:**
   * `atencion`: ForeignKey a `Atencion` (`related_name='derivaciones_auditadas'`).
   * `delegacion_origen`: ForeignKey a `Delegacion` (origen de captura).
   * `delegacion_destino`: ForeignKey a `Delegacion` (delegación responsable asignada).
   * `usuario_responsable`: ForeignKey a `Usuario` (funcionario que autoriza).
   * `motivo`: CharField descriptivo.
   * `fecha_derivacion`: DateTimeField(auto_now_add=True).
3. **Migración:** `0006_auditoriaderivacion.py` creada y aplicada en MySQL `sgr_prueba`.
4. **Django Admin:** Registrado en [`backend/core/admin.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/admin.py).

### 2.2. Backend API ([`backend/core/views.py`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py))
1. **Idempotencia:**
   * Detección por `clave_idempotencia` o cabecera `X-Idempotency-Key`.
   * Ventana temporal para mitigar dobles clics inmediatos en cliente.
2. **Control de Ámbito Territorial:**
   * Detección de alteraciones de `delegacion` ajena con rechazo 403 (`AMBITO_MANIPULADO`).
3. **Transacción Atómica y Concurrencia:**
   * `select_for_update()` en la consulta de gestiones previas de `caso_social` para prevenir condiciones de carrera (race conditions).
   * Cálculo correlativo automático de `numero_gestion` (1, 2 o 3) y bloqueo si `conteo >= 3`.
4. **Registro de Auditoría:**
   * Creación automática de `AuditoriaDerivacion` en caso de derivación inter-delegación.
5. **Serialización:**
   * Expone `clave_idempotencia`, `delegacion_responsable`, `numero_gestion` y array de `derivaciones_auditadas`.

### 2.3. Frontend ([`frontend/assets/js/modules/ingreso-atencion.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/ingreso-atencion.js))
* Generación local de token único `clave_idempotencia` (`crypto.randomUUID()`) enviado en payload y cabecera `X-Idempotency-Key`.
* Feedback visual diferenciado cuando el servidor reporta `is_duplicate_prevented` (notificación informativa SweetAlert2).
* Manejo amigable de rechazo ante intento de 4ª gestión social.

---

## 3. Matriz de Pruebas Automatizadas (`core.tests`)

Comando ejecutado: `./venv/bin/python manage.py test core`

| Caso de Prueba | Tipo | Descripción | Resultado |
|---|:---:|---|:---:|
| `test_idempotencia_previene_duplicados` | **T18** | **Misma clave de idempotencia retorna registro original sin duplicar en BD** | ✅ PASS |
| `test_prevencion_doble_envio_rapido_sin_clave` | **T18** | **Detecta doble envío consecutivo idéntico y evita duplicación** | ✅ PASS |
| `test_rechazo_ambito_manipulado_delegacion_ajena` | **T18** | **Rechaza con HTTP 403 intento de forzar delegación fuera del ámbito autorizado** | ✅ PASS |
| `test_origen_conservado_delegacion_autorizada` | **T18** | **Conserva la delegación de captura autorizada del funcionario municipal** | ✅ PASS |
| `test_responsable_autorizado_rechaza_usuario_inactivo` | **T18** | **Rechaza con HTTP 403 si el usuario responsable está inactivo** | ✅ PASS |
| `test_responsable_autorizado_rechaza_rol_inactivo` | **T18** | **Rechaza con HTTP 403 si el rol asignado al responsable está inactivo** | ✅ PASS |
| `test_caso_social_gestiones_sucesivas_1_2_3` | **T18** | **Permite registrar sucesivamente gestiones 1, 2 y 3 para un caso social** | ✅ PASS |
| `test_rechazo_cuarta_gestion_caso_social` | **T18** | **Criterio Clave: Rechaza la cuarta gestión sucesiva para un mismo caso social** | ✅ PASS |
| `test_rechazo_pareja_invalida_tipo_subtipo` | **T18** | **Rechaza con HTTP 400 si la subatención no pertenece al tipo de atención** | ✅ PASS |
| `test_derivacion_auditada_a_delegacion_responsable` | **T18** | **Derivación inter-delegación crea atención y genera registro en AuditoriaDerivacion** | ✅ PASS |
| `test_derivacion_rechaza_delegacion_responsable_inactiva` | **T18** | **Rechaza con HTTP 400 derivación hacia una delegación inactiva** | ✅ PASS |
| *(43 Pruebas previas T04, T14, T15, T16, T17)* | **Regresión Base** | **Verificación continua de CRUDs, autenticación y registro de atención** | ✅ PASS |

**Total de Pruebas Ejecutadas:** 54
**Tiempo de Ejecución:** ~0.22 segundos
**Tasa de Éxito:** 100% (54/54)
