# Pruebas del laboratorio AWS

Esta carpeta reúne el informe Word y los resultados originales del laboratorio. Su dirección evaluada fue https://50.17.79.145. Las versiones y fechas de aceptación funcional y carga son diferentes y se identifican en sus respectivos informes.

## Accesos

| Contenido | Ubicación |
|---|---|
| Informe Word de pruebas ejecutadas | [Informe_Pruebas_Ejecutadas_AWS_SGR.docx](Informe_Pruebas_Ejecutadas_AWS_SGR.docx) |
| Resultados de carga y recuperación | [rendimiento/INFORME.md](rendimiento/INFORME.md) |
| Protocolo, métricas, trazas y scripts publicados | [rendimiento/](rendimiento/) |
| Incidencias y límites | [rendimiento/INCIDENCIAS.md](rendimiento/INCIDENCIAS.md) |
| Restauración SQL aislada | [restore-resultado.json](rendimiento/restore-resultado.json) |
| Persistencia tras reinicio | [post-reinicio.json](rendimiento/post-reinicio.json) |
| Aceptación funcional y capturas | [aceptacion-funcional-local-aws/INFORME.md](aceptacion-funcional-local-aws/INFORME.md) |

## Resultados y alcance

La carga no se aprobó íntegramente: la exportación de 10.000 atenciones con diez usuarios concurrentes terminó en timeout del worker y error de servidor. La recuperación y la verificación de integridad sí tienen resultados registrados. Los escalones de veinte y cincuenta usuarios no se completaron; no se presentan como aprobados.

El informe de aceptación funcional contiene resultados de dos entornos: 316 comprobaciones AWS y 36 locales en aquella ejecución, además de la suite Django local. Los JSON cuyo nombre incluye `local` corresponden a LOCAL/QA. Se conserva el conjunto original para que puedan revisarse las comparaciones y su matriz, sin cambiar su significado.

El informe de carga registra otro recorrido posterior de 152 comprobaciones; no se suma al anterior para afirmar una cobertura integral, porque pueden compartir escenarios y tienen versiones diferentes.

El Word contiene resultados y tablas; los registros, imágenes y trazas originales se consultan en las carpetas enlazadas. Las credenciales y respaldos SQL permanecen fuera de Git.

Las 49 comprobaciones de la copia a **AWS personal** se encuentran separadas en [docs/entrega/despliegue](../../entrega/despliegue/README.md). No son una repetición de estas pruebas de carga.
