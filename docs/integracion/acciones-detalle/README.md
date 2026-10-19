# Acciones desde el detalle del registro

Versión de aplicación desplegada: `cc7c093325e79b7c104aa8e280ae23574ec613b3`.

## Corrección

El detalle de una actividad muestra «Siguiente paso», «Editar actividad» y «Adjuntar evidencia» cuando el estado y los permisos lo permiten. Al guardar, se vuelve al detalle actualizado. La carga fija la actividad de destino para evitar adjuntar al registro equivocado.

Una evidencia devuelta permite adjuntar una nueva versión desde su detalle, conservando y fijando el vínculo al respaldo anterior. Una actividad validada no ofrece edición ni carga. Los perfiles de consulta no reciben estas acciones. Los permisos y validaciones del backend se conservan.

Los compromisos abiertos permiten acceder a «Registrar seguimiento» desde el detalle o su ficha. El guardado utiliza el formulario y las transiciones existentes.

## Verificaciones

- Recorrido automatizado local con Playwright y datos ficticios: creación en QA, edición persistida, archivo vinculado a la actividad exacta, estado Pendiente, devolución por otra cuenta, nueva versión vinculada, aprobación ajena y actividad Validada. Se verificó ausencia de acciones en consulta y en actividad validada, además de vista móvil sin desbordamiento.
- El test se encuentra en `frontend/tests/detail-actions.cjs`. Requiere Playwright y tres cuentas locales preparadas: autor con edición/carga, revisor autorizado y consulta con acceso de equipo. Admite `SGR_TEST_BASE_URL`, `SGR_TEST_USER`, `SGR_TEST_REVIEWER`, `SGR_TEST_READER`, `SGR_TEST_PASSWORD` y `SGR_BROWSER_PATH`. Rechaza destinos que no sean localhost o 127.0.0.1 y solo debe ejecutarse contra una base de QA.
- [AWS personal](aws-verification.json): 9 comprobaciones aprobadas de acceso, versión, botones, editor precargado, actividad fijada, móvil, seguimiento, conservación del registro y JavaScript. Se abrieron y cancelaron formularios sin guardar cambios de negocio.
- Se revisaron las capturas de escritorio y móvil y la sintaxis JavaScript.

Despliegue acotado a nueve archivos frontend, con copia previa de archivos y configuración de versión, comprobación de huellas, salud y servicios activos. No se modificó el esquema de datos ni el laboratorio.
