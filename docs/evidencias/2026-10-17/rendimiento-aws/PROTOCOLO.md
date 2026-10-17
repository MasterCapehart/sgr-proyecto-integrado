# Protocolo ejecutado: carga, estrés limitado y recuperación

Solicitud del equipo: ejecutar las pruebas pendientes en el AWS del proyecto. Fecha: 17 de octubre de 2026, zona America/Santiago. Destino exclusivo: https://50.17.79.145, laboratorio propio. Código de aplicación evaluado: 47358a2; los commits posteriores anteriores a la ejecución solo contienen evidencias.

## Preparación y límites

- Respaldo RDS recuperable previo a los cambios, guardado privado en el servidor. No restaurar sobre la base operativa.
- Datos completamente ficticios identificados por un prefijo REN único: 10.000 atenciones D01, de las cuales 5.000 se filtran mediante G1; otras 100 en D02.
- Cincuenta cuentas con permiso de atención, delegación D01, sin privilegios de administrador, más una cuenta D02 de control. Sesiones independientes; credenciales fuera de Git.
- Una petición en curso por usuario y espera de un segundo entre operaciones. Timeout de cliente: 15 segundos. Máximo: 50 usuarios. No superar ese escalón ni agotar recursos para provocar una caída.
- Parada: más de 5 % de fallos en una ventana de 60 segundos, después del primer minuto, o inconsistencia de idempotencia. Reducir entonces a recuperación. Supervisión de salud y CPU/memoria del sistema invitado.
- Sin envío masivo de correos, sin carga sobre terceros, sin pruebas de explotación de seguridad.

## Etapas

| Etapa | Usuarios simultáneos | Duración objetivo |
|---|---:|---:|
| Control | 1 | 2 minutos |
| Carga de referencia | 10 | 10 minutos |
| Incremento | 20 | 5 minutos |
| Estrés limitado | 50 | 5 minutos |
| Recuperación | 1 | 5 minutos |

La mezcla es 50 % consulta/filtro/paginación, 20 % tablero, 20 % registro y 10 % reenvío idempotente. Se exporta el conjunto de 10.000 o más registros mientras continúa la carga de referencia. Esta mezcla adapta la propuesta B18: el 10 % de validación de evidencias se sustituye por reenvíos; por ello no acredita validación concurrente de evidencias ni cálculos de indicadores. Las duraciones son objetivos y se informa el tiempo real.

## Medición y criterios

Se registran cada petición, etapa, operación, código HTTP, tiempo de extremo a extremo desde el computador de prueba, bytes y error. Se calculan promedio, p95, p99, máximo, peticiones/s y excedencias sobre 2 y 5 segundos. Se compara consulta/registro con 2 s y tablero con 5 s como referencias S1; no se presenta esa carga como aceptada contractualmente por el docente. No existe umbral aprobado de exportación.

La primera consulta se identifica como primera observada, con estado de caché desconocido. No se vacían cachés de la base operativa; no acredita caché fría. La captura de CPU/memoria es del EC2 invitado; no sustituye CloudWatch, métricas RDS, conexiones MySQL ni créditos de CPU.

Después se concilian los conteos y claves confirmadas, se comprueba nuevo inicio de sesión y aislamiento de delegaciones. La recuperación de carga no equivale a restaurar un respaldo. Disponibilidad mensual, RPO, RTO, restauración y rollback solo se acreditan si se ejecutan por separado y se documentan.
