# Resultados de las pruebas AWS

**Resultado general: no aprobado íntegramente.** Se detectó una falla real de exportación masiva durante carga concurrente. El sistema se recuperó y las verificaciones de integridad y restauración pasaron.

Ejecución: 17 de octubre de 2026, America/Santiago. Código de aplicación: `47358a26167f4efb0a4fe0638e78d815f821967a`. Destino: HTTPS del laboratorio del proyecto. Solicitud del equipo: ejecutar las pruebas de AWS pendientes. Son datos ficticios QA, no información institucional confirmada.

## Resumen de ejecución

| Prueba | Resultado observado | Estado |
|---|---|---|
| Consulta de lotes de 5.000 y 10.000 | Filtros, páginas y conteos correctos; primera consulta con caché desconocida | Aprobada en alcance observado |
| Control con 1 usuario | 120,09 segundos, 66 solicitudes, 0 fallos | Aprobada |
| 10 usuarios y exportación masiva | 35,03 segundos, 97 solicitudes, 11 fallos desde cliente; exportación termina en timeout de worker y HTTP 500 en servidor | Fallida e interrumpida |
| 20 y 50 usuarios | No se ejecutaron después de la degradación | Pendiente |
| Recuperación con 1 usuario | 301,87 segundos, 169 solicitudes, 0 fallos | Aprobada en ventana observada |
| Integridad de escrituras | 67 confirmaciones y 67 filas; ningún ID ausente/distinto, clave duplicada, autor o delegación incorrectos | Aprobada |
| Aislamiento D01/D02 | 10.000 semillas y 67 nuevas en D01; 100 en D02; cuenta D02 solo ve sus 100 | Aprobada |
| Recorrido funcional posterior | 152 comprobaciones aprobadas, incluyendo registro, persistencia, permisos, carga y aprobación de evidencia S3 y cierre de sesión | Aprobada con adaptación de cuentas QA |
| Restauración de respaldo | 39 tablas y 11.194 filas; conteos y checksums iguales, copia temporal eliminada | Aprobada como ensayo aislado |
| Persistencia tras reinicio | 8 comprobaciones aprobadas: login, contexto, atención, aprobación, archivo S3, conteos D01/D02 y salud RDS | Aprobada |

Las solicitudes y comprobaciones funcionales son unidades diferentes: no se suman para presentar una cifra artificial de casos. La fase de carga generó 342 solicitudes incluyendo preparación y conciliación. Once fallaron, todas en el escenario combinado de diez usuarios y exportación. La prueba se detuvo por un reenvío sin respuesta confirmada; no llegó a completar el minuto de la regla de tasa de errores. Ver limitación del ejecutor en INCIDENCIAS.md.

## Tiempos de extremo a extremo

| Operación | Etapa | Promedio | p95 | Máximo | Fallos |
|---|---|---:|---:|---:|---:|
| Consulta/filtro/página | Control | 1.069 ms | 1.391 ms | 1.625 ms | 0/27 |
| Registro | Control | 662 ms | 711 ms | 711 ms | 0/11 |
| Tablero | Control | 631 ms | 685 ms | 685 ms | 0/17 |
| Consulta/filtro/página | 10 usuarios + exportación | 2.952 ms | 15.186 ms | 15.405 ms | 6/48 |
| Registro | 10 usuarios + exportación | 2.278 ms | 15.003 ms | 15.003 ms | 2/19 |
| Tablero | 10 usuarios + exportación | 1.494 ms | 1.340 ms | 15.003 ms | 1/21 |
| Consulta/filtro/página | Recuperación | 992 ms | 1.100 ms | 1.116 ms | 0/70 |
| Registro | Recuperación | 644 ms | 732 ms | 796 ms | 0/39 |
| Tablero | Recuperación | 633 ms | 673 ms | 761 ms | 0/36 |

Percentiles de rango más cercano; `metricas.csv` incluye p99 y excedencias. El tablero con p95 bajo en la etapa de diez usuarios igualmente falla por su máximo y error. Los tiempos de fallos incluyen espera del cliente, no una respuesta HTTP completa. El timeout de exportación del cliente fue 15 segundos; el registro independiente del servidor confirma que tampoco terminó antes del timeout de worker de 90 segundos. No se recibió un Excel íntegro.

## Recursos y restauración

Se capturaron 64 muestras del EC2 invitado: CPU máxima observada 52,08 % y memoria disponible mínima 1.364,81 MiB. Estos valores no prueban ausencia de otros cuellos de botella ni reemplazan métricas de RDS o créditos de CPU.

Se generó un nuevo respaldo privado de 2.642.736 bytes y se restauró en un esquema QA temporal separado, con la aplicación detenida para comparar un estado estable. Importación: 3,98 segundos. Ventana del procedimiento con servicio detenido: 13,574 segundos; el acceso efectivo se verificó posteriormente, por lo que esa cifra no es una medición exacta de indisponibilidad de extremo a extremo. Se compararon conteos y checksums de las 39 tablas. La base operativa nunca se reemplazó. El esquema temporal se eliminó y el servicio se inició. Esto ensaya un respaldo SQL y reinicio, no un rollback completo de versión ni una restauración desde snapshot RDS ante desastre.

## Trazabilidad con el documento

| Caso | Conclusión |
|---|---|
| REN-01 | Parcial: volumen, filtros, páginas y tiempos medidos; caché fría y diez minutos normales pendientes. |
| REN-02 | Fallo observado durante escenario combinado; recuperar y repetir después de corrección. |
| REN-03 | Fallido: exportación de 10.000 registros no completada. |
| REN-04 | Integridad de 67 escrituras concurrentes y reenvíos comprobada; no cubre sobrescritura concurrente de todos los módulos. |
| REN-05 | Degradación observada bajo diez usuarios más exportación; capacidad máxima y escalones 20/50 no determinados. |
| REN-06 | Recuperación de cinco minutos, conciliación y recorrido posterior con aprobación comprobados; no se validan cálculos de indicadores excluidos. |
| AWS-01 | HTTPS, salud y versión consultados; observación limitada al momento del ensayo. |
| AWS-03 | Persistencia y archivos después de reinicio comprobados; falla de exportación masiva impide aprobación global. |
| AWS-04 | Registro, evidencia, aprobación y persistencia comprobados; incremento de motor de cálculo no evaluado. |
| AWS-05 | No se repitió auditoría completa de red/infraestructura; no se acredita con este informe. |
| AWS-06 | Respaldo SQL y restauración aislada aprobados; rollback de versión y despliegue desde clon limpio no ensayados aquí. |

## Incidencias del ejecutor y pendientes

El recorrido funcional inicial aprobó 107 comprobaciones y se detuvo ante el rechazo 401 al usar la cuenta guardada `verificador.aws`. La comprobación posterior mostró esa cuenta inactiva, con rol y delegación activos: el rechazo es coherente con su estado y no demuestra un defecto de autenticación. Se retomó el mismo conjunto QA con verificadores ficticios nuevos y se completaron 152 comprobaciones acumuladas, sin restablecer cuentas personales. No se presenta el primer intento como una ejecución completa sin interrupciones.

El resumen original del ejecutor se conserva por auditoría. Sus percentiles usan una posición inferior y su etiqueta de idempotencia es imprecisa; las métricas definitivas están recalculadas en `metricas.csv` y la integridad se decide con `integridad-resultado.json`.

Primero corresponde corregir e investigar la exportación masiva. Después se repiten diez usuarios con exportación y, si la etapa se mantiene estable, se ejecutan veinte y cincuenta usuarios, la mezcla de validación de evidencias y la recuperación. No se acredita cumplimiento al 100 %, disponibilidad mensual ni objetivos contractuales de RPO/RTO.
