# Código visible al abrir el formulario — AWS, 20/10/2026

Versión: `7f65cf6ad9d68a090fe340026afa7eee3030cf50`.

Los seis mantenedores solicitan al servidor una reserva al pulsar Nuevo. El campo Código muestra el valor definitivo, de solo lectura, antes de guardar. La prueba funcional comprobó en los seis catálogos que el valor reservado coincide exactamente con el persistido. Cancelar conserva una reserva auditable sin crear una fila vacía del catálogo. Los códigos de reserva usan un prefijo como DEL-R000123 y pueden presentar saltos.

Se verificaron 14 archivos por SHA-256, salud/versión y servicios activos. Antes del despliegue se prepararon copias de archivos/configuración y un volcado de base de 2.729.482 bytes, cifrado en S3 privado. No hubo migraciones ni renumeración de registros existentes.

Validación local: regresión de 387 casos (386 aprobados y un fallo esperado preexistente), seis pruebas específicas de reservas y recorrido de navegador aprobados.

Validación remota: 12 comprobaciones funcionales aprobadas, incluyendo reserva/guardado del mismo código en los seis catálogos, conservación de códigos anteriores y regresión de registros operativos/casos sociales. El ensayo se revirtió transaccionalmente; la comparación de códigos y asignaciones anteriores coincidió. No quedaron registros del catálogo de ese ensayo.

Navegador HTTPS: ocho comprobaciones aprobadas, incluyendo código visible en los seis formularios; sin errores JavaScript observados. Abrir los seis formularios registra seis reservas en auditoría; se cerraron sin guardar registros del catálogo.

- [Resultado funcional](functional-verification.json)
- [Resultado de navegador](browser-verification.json)
- [Captura en AWS](aws-codigo-visible.png)
