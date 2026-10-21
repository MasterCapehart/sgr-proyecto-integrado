# Simplificación del tubo — validación local

Estado: preparado en local; no desplegado en AWS.

- Formulario de compromiso dividido en datos de solicitud, responsable/plazo y seguimiento (al editar).
- Área o persona de apoyo opcional; se deja vacía cuando no hay apoyo adicional. No se completa con el área del cargo.
- Unidad y código verificador retirados del formulario de compromiso. Los datos históricos se conservan; la unidad permanece en 1 y el código del origen se reutiliza al crear desde una atención/actividad.
- Responsable propuesto: usuario actual. Se conservan las validaciones de delegación, permisos, fecha y seguimiento.
- El registro unificado y la captura anterior de seguimiento también permiten omitir apoyo.

## Verificación

38 pruebas automatizadas aprobadas (23 de captura/vinculación y 15 del dominio). Las dos pruebas nuevas fallaron antes del cambio y pasaron después. Navegador local: alta de actividad ficticia con compromiso, solicitud/contacto/sector/código conservados, unidad 1, apoyo vacío, formulario nuevo y seguimiento, móvil sin desbordamiento. No se modificaron registros AWS. Migración 0021 preparada; aplicada únicamente a la base SQLite del entorno de vista previa.

Abrir http://127.0.0.1:8013/pages/tubo-trabajo.html y pulsar «+ Nuevo compromiso» o «Seguimiento». Para probar el origen: http://127.0.0.1:8013/pages/registro-trabajo.html y seleccionar ingreso al tubo.
