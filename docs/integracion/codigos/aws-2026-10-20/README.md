# Códigos automáticos en AWS — 20/10/2026

Versión de aplicación: `19e31833f4e920327896906792d973ad342ab978`.
URL: https://54.236.112.203/pages/login.html
Entorno: cuenta AWS personal. El laboratorio no se modificó.

## Aplicación y respaldo

Se integró y publicó el código en `main`, sin solicitud de revisión. Se verificaron por SHA-256 los 24 archivos de aplicación del paquete y sus versiones anteriores. Antes del cambio se prepararon copias de archivos/configuración y un volcado de base de datos de 2.729.051 bytes, conservado en el servidor y respaldado con cifrado AES256 en S3 privado. El volcado y las credenciales no se incluyen en Git.

La comprobación de Django y la revisión de migraciones pendientes aprobaron; no se modificó el esquema. Servicios SGR y Nginx activos, salud y versión publicadas verificadas. Los códigos anteriores no se convirtieron ni renumeraron.

## Comprobaciones funcionales en AWS

Doce comprobaciones aprobadas sobre la base remota utilizando las vistas de la API desplegada, dentro de una transacción revertida al finalizar:

1. Delegación nueva sin código manual.
2. Cargo nuevo sin código manual.
3. Ítem nuevo sin código manual.
4. Tipo nuevo sin código manual.
5. Período nuevo sin código manual.
6. Subatención nueva sin código manual.
7. Edición de un registro anterior conservando su código.
8. Actividad con prefijo de área, fecha e identificador.
9. Compromiso con folio y referencia de foto automáticos.
10. Atención con folio y caso social generados automáticamente.
11. Reintento de apertura sin duplicados.
12. Continuidad del mismo caso, conservación de las tres gestiones y rechazo de una cuarta.

Se compararon antes y después los identificadores y códigos de los diez modelos implicados, además de los cargos/roles asignados a usuarios. La comparación coincidió tras revertir la transacción. No quedaron registros de negocio de estas pruebas. Las secuencias internas pueden avanzar aunque una transacción se revierta; no son secuencias sin saltos. El rechazo HTTP 409 de la cuarta gestión fue el resultado esperado.

Resultados: [functional-verification.json](functional-verification.json).

## Recorrido de interfaz por HTTPS

Ocho verificaciones aprobadas: los seis mantenedores muestran el código de solo lectura y «Se genera al guardar»; Gestión social permite nuevo caso automático; la referencia de foto del compromiso es de solo lectura. No se guardaron formularios durante este recorrido. No hubo errores JavaScript observados.

Resultados: [browser-verification.json](browser-verification.json).

Estos resultados complementan la regresión local de 382 casos (381 aprobados y un fallo esperado preexistente). No se presentan como repetición integral de toda la batería funcional en AWS. El código FOTO por sí mismo no acredita un archivo adjunto; las evidencias se siguen cargando y revisando en su módulo.
