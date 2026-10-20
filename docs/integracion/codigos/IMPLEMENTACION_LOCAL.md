# Códigos automáticos — implementación local

Los códigos se generan en el servidor al guardar registros nuevos. Las claves primarias asignadas por la base de datos aportan el consecutivo; no se calcula con MAX+1 ni con el total de filas. Puede haber saltos y no se promete una secuencia por día o por delegación.

## Formatos

| Registro nuevo | Ejemplo ficticio | Regla |
| --- | --- | --- |
| Delegación | DEL-000123 | DEL + identificador interno |
| Cargo / área | CAR-000123 | CAR + identificador interno |
| Ítem | ITM-000123 | ITM + identificador interno |
| Tipo de atención | TIP-000123 | TIP + identificador interno |
| Subatención | SUB-000123 | SUB + identificador interno |
| Período | PER-000123 | PER + identificador interno |
| Actividad | COM2-20261020-000123 | Prefijo del cargo, fecha de actividad e identificador |
| Atención | AT-20261020-000123 | Fecha de ingreso e identificador |
| Caso social nuevo | CS-20261020-000123 | Fecha de apertura e identificador del expediente |
| Compromiso | TUB-20261020-000123 | Fecha de solicitud e identificador |
| Referencia de foto del compromiso | FOTO-20261020-000123 | Fecha de solicitud e identificador del compromiso |

Los prefijos de áreas siguen lo encontrado en el Excel, incluido SOC/SCO. Si un cargo no permite determinar un prefijo conocido se usa ACT, sin inventar una numeración territorial. Año, separadores y clave primaria son una adaptación al sistema web, no el formato literal del libro. Los prefijos de catálogos son decisiones técnicas, pues el Excel no define esos códigos.

## Conservación y compatibilidad

- Se conservan los códigos anteriores; editar un registro, su nombre o su fecha no recalcula su código.
- Los seis formularios de catálogos muestran «Se genera al guardar» en un campo de solo lectura. La creación por API sin código o con código vacío lo genera; se mantiene compatibilidad con integraciones que proporcionan códigos explícitos. Los formatos inválidos y duplicados explícitos siguen rechazándose.
- Un código propuesto que ya esté ocupado por un registro histórico utiliza un sufijo aleatorio de reserva. La restricción única de la base impide duplicados y se reintenta dentro de una transacción aislada.
- No se cambian las claves primarias ni las relaciones, auditorías o capturas históricas. La auditoría de altas guarda el código definitivo.
- No requiere migraciones del esquema. No se hizo una conversión masiva de los registros existentes.
- La referencia FOTO identifica el registro; por sí sola no acredita una fotografía. El archivo se sigue adjuntando y revisando mediante Evidencias. Se conservan las referencias de foto antiguas.

## Gestión social

El formulario permite atención sin expediente, crear caso nuevo con código automático o seleccionar un expediente existente. El código no se escribe manualmente. La continuación desde Gestión social rellena el mismo caso y conserva el límite de tres gestiones, los controles de solicitante/delegación y la clave de idempotencia. Un reintento de la apertura no crea otro expediente.

Los códigos de recuperación de contraseña continúan introduciéndose desde el correo: son verificaciones de acceso, no identificadores de registros.

## Validación

`backend/core/test_auto_codes.py` verifica altas sin código de los seis catálogos, conservación de anteriores, actividad por área/fecha, estabilidad al editar, compromiso y foto automáticos, apertura/continuación de caso con reintento y límite de tres gestiones, entrada inválida y colisión con código histórico. Incluye una prueba de cuatro altas simultáneas con códigos distintos.

Se ajustaron las pruebas antiguas que exigían código manual como campo obligatorio; las verificaciones de nombres, relaciones, formatos y códigos duplicados explícitos permanecen activas.

Regresión completa en MySQL: 382 casos, 381 aprobados y un fallo esperado preexistente; sin fallos inesperados. Comprobación de Django sin incidencias.

Recorrido en navegador sobre base QA independiente: delegación creada sin código manual, código persistido, caso nuevo automático, continuación con el mismo código y referencia de foto de solo lectura. Sin errores JavaScript durante el recorrido.

Esta etapa está implementada en local y no se ha desplegado en AWS. Las pruebas usan cuentas y datos ficticios.
