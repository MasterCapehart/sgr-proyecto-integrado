# Pruebas del SGR

Documentos y evidencias reunidos para revisar directamente las pruebas locales y las ejecutadas en el laboratorio AWS. Los archivos fuente se copiaron sin modificar; el historial anterior se conserva.

| Contenido | Ubicación |
|---|---|
| Fichas Word, informe de pantallas, capturas, Excel y regresiones locales | [local/](local/README.md) |
| Informe Word, aceptación funcional, carga, integridad, restauración y reinicio del laboratorio AWS | [aws/](aws/README.md) |
| Informe de cierre aportado por el equipo | [Informe_Cierre_Pruebas_SGR (1).docx](Informe_Cierre_Pruebas_SGR%20%281%29.docx) |

El informe de cierre se encuentra directamente en esta carpeta, fuera de `local/` y `aws/`, según la organización acordada. Se conserva exactamente el archivo entregado; sus cifras y pendientes corresponden a las fuentes y fechas que declara, no a una consolidación recalculada de todos los resultados posteriores.

## Interpretación

- LOCAL/QA y AWS son entornos distintos; no se suman comprobaciones, solicitudes HTTP y casos del plan como si fueran una misma unidad.
- La carga del laboratorio encontró una falla de exportación masiva y no acredita cumplimiento integral. Se incluyen el fallo, la recuperación y la conciliación de datos.
- La carpeta de aceptación funcional combina resultados locales y AWS; su informe y sus archivos identifican el entorno. No atribuir los JSON `local-resultados-ui` y `resultados-metas-local` ni la suite Django local a una ejecución remota.
- Las verificaciones del traslado a la cuenta personal permanecen diferenciadas en [docs/entrega/despliegue](../entrega/despliegue/README.md). No se presentan como nuevas pruebas de carga del laboratorio.
- [docs/entrega](../entrega/README.md) conserva la revisión de cobertura y pendientes. Esta recopilación no significa aprobación al 100 % ni aceptación del docente.

`manifest.json` registra el origen, tamaño y SHA-256 de los 281 archivos copiados. No se incluyen entornos privados, contraseñas, cookies de navegador, volcados SQL ni credenciales AWS.
