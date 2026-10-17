# Evidencias de carga y recuperación AWS

Leer primero [INFORME.md](INFORME.md). **La ejecución encontró un fallo real de exportación y no acredita cumplimiento completo.**

- `PROTOCOLO.md`: destino, datos, escenarios y límites definidos antes de ejecutar.
- `metricas.csv`: promedio, p95, p99, máximo, errores y excedencias por etapa/operación; percentiles de rango más cercano.
- `solicitudes.jsonl`: traza de 342 solicitudes, sin contraseñas ni cookies. Estado 0 = el cliente no obtuvo respuesta HTTP.
- `resumen.json`: resumen revisado; `resumen-ejecutor-original.json` conserva las limitaciones del ejecutor original descritas en `INCIDENCIAS.md`.
- `recursos.jsonl` y `recursos-resumen.json`: mediciones del EC2 invitado; no son datos CloudWatch/RDS.
- `integridad-resultado.json`: conciliación directa de 67 nuevas atenciones y semillas de volumen.
- `funcional-posterior.json`: 152 comprobaciones funcionales acumuladas; el intento inicial se interrumpió por cuenta QA inactiva y se completó mediante continuación con verificadores nuevos.
- `restore-resultado.json`: restauración SQL en esquema temporal, conteos y checksums de 39 tablas.
- `post-reinicio.json`: ocho verificaciones de persistencia, acceso y archivo S3 después del reinicio.
- `cleanup-resultado.json`: 54 cuentas ficticias objetivo, 53 todavía activas al terminar; ninguna de esas cuentas queda activa. La preparación y cierre de fixtures se hacen por ORM y no se cuentan como pruebas de mantenedores. Los datos QA permanecen identificados en sus delegaciones de prueba.
- `scripts/`: preparación, ejecutor exacto de carga, monitor, verificación de integridad y ensayo de restauración. Requieren las configuraciones privadas del operador; no incluyen credenciales. El ejecutor exacto contiene la etiqueta imprecisa explicada en INCIDENCIAS.md: no reutilizar esa etiqueta como prueba de corrupción.

El ensayo de restauración detiene temporalmente el servicio, crea y elimina únicamente un esquema con prefijo `sgr_restore_qa_`, y conserva el respaldo privado. Solo se debe ejecutar en el laboratorio autorizado y con los archivos privados preparados. No ejecutar estos scripts contra producción o terceros.

Se retiraron del servidor los archivos temporales de credenciales y scripts. Los respaldos SQL quedan privados en `/srv/sgr/backups`, fuera del repositorio. No se cambió el código de aplicación ni se abrió una solicitud de revisión.
