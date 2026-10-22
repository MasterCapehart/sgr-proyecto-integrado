# Plazos y cupos diarios

Estado: implementado y verificado en local el 22/10/2026. Pendiente de despliegue. No calcula ni concede puntaje.

## Comportamiento

- Se permite completar los requisitos de candidatura durante tres fechas calendario inclusivas: una actividad realizada el lunes puede quedar candidata hasta el miércoles. Desde el jueves se conserva para trazabilidad, sin aportar a puntos ni metas. Se incluyen fines de semana y se utiliza America/Santiago.
- Máximo siete actividades potencialmente puntuables por autor y fecha de realización, sumando sus delegaciones. La octava se rechaza claramente y no deja actividad, ficha social ni compromiso parcialmente creados.
- Los registros no elegibles y los tardíos pueden conservarse sin consumir cupo. Las candidaturas dependen del catálogo explícito, los datos de contacto y la exclusión del delegado como beneficiario implementados en el bloque anterior.
- Al quitar los requisitos de candidatura se libera el cupo. Recuperarla exige un cupo disponible y estar aún dentro del plazo. Correcciones de texto posteriores y revisiones de evidencias no eliminan una candidatura conseguida a tiempo.
- La fecha de realización queda fija después del primer guardado. No existe excepción especial de reapertura en este incremento.
- Los estados Borrador, Pendiente, Validada, Corrección y Rechazada conservan cupo mientras la actividad siga candidata. Una evidencia anulada no equivale a cancelar la actividad.
- No se reclasifica el historial: las candidaturas anteriores ya evaluadas cuentan conservadoramente para nuevos registros del mismo autor/día. El historial sin evaluación no consume cupo.

## Interfaz

El registro común muestra la fecha límite, los cupos disponibles al consultar y el motivo del bloqueo. La comprobación definitiva se repite al guardar. El detalle conserva el control de plazo y reserva; al editar, la fecha aparece deshabilitada.

## Implementación y consistencia

Migración `0025_plazos_cupos`: fila de control por funcionario y bandera de reserva en Actividad. La política aplicada se conserva en `elegibilidad_snapshot.control_registro`.

La fila de control se crea antes de la transacción de negocio. Después se bloquea dentro de ella para serializar altas y correcciones del mismo autor. Esto evita tanto exceder siete con solicitudes simultáneas como el bloqueo detectado al crear por primera vez el control. Los reintentos de una misma captura siguen devolviendo el mismo registro.

## Verificación local

- 25 pruebas específicas de plazo, cupos, concurrencia, códigos e idempotencia: correctas.
- Suite completa: 488 pruebas, correcta con una prueba marcada como fallo esperado preexistente.
- Navegador: séptima aceptada, octava rechazada, liberación de cupo, conservación tardía sin elegibilidad, vista previa y pantalla móvil sin errores JavaScript ni desbordamiento horizontal.
- Modelos y migraciones coherentes; revisión de espacios del diff correcta.

No se ejecutó despliegue, no se modificaron diagramas ni se integraron los bloques de felicitaciones, ausencias, tope del 120 % o indicadores colectivos.
