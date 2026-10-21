# Permisos por Rol y Recorrido de Trabajo — Validación Local y AWS

Fecha: 21 de octubre de 2026.
Entorno evaluado: Local (Django / MySQL) y AWS Personal (`54.236.112.203`).

## 1. Definición y Reglas de Permisos por Rol

| Rol | Alcance y Capacidades | Restricciones Comprobadas |
|---|---|---|
| **Funcionario** | Registrar trabajo operativo y social (`actividades.crear`, `actividades.editar`, `atenciones.crear`), iniciar seguimiento en el tubo (`compromisos.crear`), adjuntar evidencias propias (`evidencias.crear`) y consultar pendientes personales (`/api/mi-progreso/`). | Bloqueo absoluto de administración (`roles`, `usuarios`, `delegaciones`, `periodos`, `auditoria`). Sin acceso a bandeja de validación (`evidencias.revisar` denegado). Los catálogos autorizados solo para lectura aparecen en «Catálogos de consulta». «Administración» se muestra únicamente si hay otros accesos autorizados; los catálogos con permiso de crear, editar o desactivar permanecen allí. |
| **Verificador** | Consultar evidencias de la delegación activa (`evidencias.ver`, `evidencias.ver_equipo`), bandeja de validación y revisión de evidencias ajenas (`evidencias.revisar`), solicitar correcciones, aprobar o rechazar con observación obligatoria. | Bloqueo de auto-revisión (el autor de la actividad/evidencia no puede auto-aprobarse). Sin acceso administrativo ni creación de actividades. |
| **Delegado / Coordinador** | Consultar y dar seguimiento al avance de todo el equipo de su delegación activa (`actividades.ver_equipo`, `compromisos.ver_equipo`, `evidencias.ver_equipo`). Editar y reasignar compromisos del equipo (`compromisos.editar`, `compromisos.editar_equipo`) con historial de auditoría. | Sin permisos de administración global de usuarios ni roles del sistema. |
| **Consulta** | Visualizar y exportar registros y compromisos de la delegación activa (`*.ver`, `*.ver_equipo`, `*.exportar`). | Cero escritura: bloqueado ante cualquier creación, edición o revisión (`403 Forbidden`). En frontend se ocultan todos los botones de alta o modificación. |

## 2. Recorrido Integral Verificado

Se validó el ciclo completo `Registro → Tubo → Evidencia → Revisión → Corrección → Aprobación`:
1. **Registro**: Funcionario crea actividad y solicita seguimiento al tubo mediante captura unificada (`POST /api/captura/`). Se asignan correlativos y folio de compromiso.
2. **Tubo de trabajo**: El compromiso se crea vinculado al código de la actividad y queda disponible en la agenda colectiva (`/api/operacion/compromisos/`).
3. **Evidencia**: Funcionario adjunta archivo PDF de respaldo (`POST /api/operacion/evidencias/`). La actividad pasa a estado `Pendiente`. Se verifica que el funcionario no puede auto-aprobarse.
4. **Revisión**: Verificador ajeno revisa la evidencia en la bandeja de validación y solicita `Corrección` con observación obligatoria ("Falta acta de firmas"). La evidencia y la actividad pasan a estado `Corrección`.
5. **Corrección**: Funcionario consulta `/api/mi-progreso/` y ve la tarea en corrección. Adjunta nueva versión corregida indicando `reemplaza: <id_evidencia_devuelta>`. La evidencia anterior se conserva no vigente en el historial y la actividad vuelve a quedar en `Pendiente`.
6. **Aprobación final**: Verificador revisa la nueva versión y aprueba (`Aprobada`) con observación conforme. La actividad pasa a estado `Validada` y queda protegida contra futuras alteraciones.

## 3. Pruebas Automatizadas

* **Suite local dedicada**: `backend/core/test_role_permissions_workflow.py` (8 pruebas aprobadas al 100%).
* **Regresión local global**: 436 pruebas ejecutadas (`435 OK`, `1 expected failure` heredada).
* **Verificación transaccional en AWS**: 27 comprobaciones aprobadas en vivo sobre EC2/RDS personal (`54.236.112.203`) mediante SSM y transacción atómica con rollback limpio, sin residuos ficticios en la base de datos.

## Ajuste del menú (validado en local)

Los accesos de lectura a Ítems y metas, Tipos de atención y Subatenciones se agrupan en «Catálogos de consulta». No se retiran ni conceden permisos de API. La clasificación usa permisos de cada catálogo y no el nombre del rol; admite permisos mixtos sin enlaces duplicados. El grupo Administración desaparece si no contiene accesos.
