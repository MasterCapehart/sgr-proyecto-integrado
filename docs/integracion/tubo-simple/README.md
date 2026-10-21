# Simplificación del tubo — validación local

Estado: desplegado en AWS personal el 21/10/2026. Versión de aplicación: `a0c62d8068ea83ab4d80a3af4c2a4695986a31f3`.

- Formulario de compromiso dividido en datos de solicitud, responsable/plazo y seguimiento (al editar).
- Área o persona de apoyo opcional; se deja vacía cuando no hay apoyo adicional. No se completa con el área del cargo.
- Unidad y código verificador retirados del formulario de compromiso. Los datos históricos se conservan; la unidad permanece en 1 y el código del origen se reutiliza al crear desde una atención/actividad.
- Responsable propuesto: usuario actual. Se conservan las validaciones de delegación, permisos, fecha y seguimiento.
- El registro unificado y la captura anterior de seguimiento también permiten omitir apoyo.

## Verificación

38 pruebas automatizadas aprobadas (23 de captura/vinculación y 15 del dominio). Las dos pruebas nuevas fallaron antes del cambio y pasaron después. Navegador local: alta de actividad ficticia con compromiso, solicitud/contacto/sector/código conservados, unidad 1, apoyo vacío, formulario nuevo y seguimiento, móvil sin desbordamiento. No se modificaron registros AWS. Migración 0021 preparada; aplicada únicamente a la base SQLite del entorno de vista previa.

Abrir http://127.0.0.1:8013/pages/tubo-trabajo.html y pulsar «+ Nuevo compromiso» o «Seguimiento». Para probar el origen: http://127.0.0.1:8013/pages/registro-trabajo.html y seleccionar ingreso al tubo.

## Despliegue AWS personal

URL: https://54.236.112.203/pages/tubo-trabajo.html?v=tubo-simple-1

Copia previa de archivos y respaldo SQL cifrado en S3 (2.772.306 bytes). Migración 0021 aplicada; salud, versión, hashes y servicios verificados.

49 comprobaciones transaccionales aprobadas en AWS, con rollback final y sin datos QA persistidos. Incluyen captura general/social, apoyo vacío, edición sin apoyo, unidad automática, datos del origen, reintentos, permisos y aislamiento por delegación.

Navegador AWS: alta de compromiso organizada, unidad/código fuera del formulario, apoyo opcional, vista móvil y captura con apoyo vacío. No se guardaron registros desde el navegador. La cuenta de prueba no tenía compromisos editables en el listado; la edición se comprobó mediante el ensayo transaccional y en el navegador local.
