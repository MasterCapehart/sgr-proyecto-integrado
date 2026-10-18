# Verificación documental de la entrega SGR

Revisión del paquete mínimo de evidencias de B21, página 25 de los requisitos de segunda evaluación. Esta revisión comprueba los archivos disponibles; no ejecuta una nueva carga ni convierte pruebas pendientes en aprobadas.

## Resultado de la revisión

**La documentación contiene evidencia real, pero el paquete todavía no está completo ni aprobado al 100 %.** La exportación masiva falló en el laboratorio y no hay evidencia de su corrección y repetición satisfactoria. El motor definitivo de metas y semáforos permanece excluido del incremento implementado.

| Elemento solicitado | Estado comprobado | Evidencia y limitación |
|---|---|---|
| Resultados de carga | Parcial; hay una ejecución fallida | [Informe del laboratorio](../.archivo/interno/2026-10-17/evidencias/rendimiento-aws/INFORME.md), [métricas](../.archivo/interno/2026-10-17/evidencias/rendimiento-aws/metricas.csv) y [traza](../.archivo/interno/2026-10-17/evidencias/rendimiento-aws/solicitudes.jsonl). Control y recuperación completados; diez usuarios más exportación se interrumpieron. Escalones 20/50 no ejecutados. |
| Cálculos independientes de métricas | Disponibles y reproducidos | [Método de revisión](calculos/README.md), [script](calculos/recalcular_metricas.py), [resultado](calculos/verificacion_calculos.json) y [CSV recalculado](calculos/metricas_recalculadas.csv). Se revisaron las 342 solicitudes, 11 fallidas y 18 grupos; todos coinciden con las métricas publicadas. |
| Cálculos independientes de metas, ponderaciones y semáforos | Pendientes | Las métricas de carga no sustituyen CAL-01 a CAL-05 ni los resultados esperados del motor. No hay evidencia suficiente para aprobarlos. Deben justificarse en el alcance y no contarse como aprobados. |
| Registro de incidencias | Disponible | [REN-EXP-01 y límites del ejecutor](../.archivo/interno/2026-10-17/evidencias/rendimiento-aws/INCIDENCIAS.md): exportación de 10.000 atenciones sin Excel completo, timeout del worker y degradación. La etiqueta inicial de idempotencia fue rectificada mediante verificación de MySQL, sin evidencia de corrupción de datos. |
| Evidencias de corrección y regresión | Parciales | [Implementación y evidencias locales de períodos y conciliación](../.archivo/interno/2026-10-17/evidencias/periodos-local/README.md), [salida de 344 pruebas](../.archivo/interno/2026-10-17/evidencias/periodos-local/regresion-344.txt) y [conciliación histórica](../.archivo/interno/2026-10-17/evidencias/periodos-local/conciliacion-historica.txt). Son 343 aprobadas y una falla esperada heredada. No acreditan una corrección de REN-EXP-01 en AWS. |
| URL AWS de entrega | Disponible; última comprobación 18/10/2026 | [Cuenta personal](https://54.236.112.203/pages/login.html). Se conserva separado el [laboratorio](https://50.17.79.145/pages/login.html). La disponibilidad posterior depende de que los servicios sigan operativos. |
| Commit evaluado | Identificado | Aplicación desplegada y evaluada: [`47358a26167f4efb0a4fe0638e78d815f821967a`](https://github.com/MasterCapehart/sgr-proyecto-integrado/commit/47358a26167f4efb0a4fe0638e78d815f821967a). [Consulta de versión](https://54.236.112.203/api/version/). Los commits posteriores de documentación no equivalen a un nuevo despliegue. |
| README e instrucciones | Disponibles; ensayo de clon limpio pendiente | [README principal](../../README.md), [instalación local](../../backend/README.md), [guía del despliegue personal](despliegue/README.md) y [guía original del laboratorio](../../deploy/aws/README.md). No se presenta la instalación desde copia del servidor como un ensayo desde clon limpio. |
| Evidencia de instalación AWS personal | Disponible en alcance de copia | [Dependencias instaladas](despliegue/evidencias/instalar-destino.txt), [configuración inicial](despliegue/evidencias/configurar-destino.txt) y [comprobación final](despliegue/evidencias/final-destino.txt). La configuración inicial terminó con un 502 al arrancar; las comprobaciones posteriores acreditan salud y versión correctas. No se oculta ese intento. |
| Respaldo e integridad | Disponibles | [Restauración en la copia personal](despliegue/evidencias/database-verification.json): 39 tablas coincidentes antes de las pruebas web. [Evidencias S3 copiadas](despliegue/evidencias/s3-copy-manifest.json). Los SQL y las credenciales quedan privados. |
| Recuperación y persistencia | Parciales según entorno | [Restauración SQL aislada del laboratorio](../.archivo/interno/2026-10-17/evidencias/rendimiento-aws/restore-resultado.json): 39 tablas y 11.194 filas. La copia personal contiene un respaldo posterior de 11.201 filas. [Reinicio personal](despliegue/evidencias/reboot-verification.json): salud y versión correctas. No se ensayó recuperación desde snapshot RDS ante desastre ni reversión completa de versión. |
| Comprobaciones de traslado personal | Disponibles; no sustituyen la aceptación completa | [49 comprobaciones](despliegue/evidencias/web-verification.json). Incluyen acceso, contexto, consultas, exportaciones pequeñas, conversación y descarga de evidencia. No acreditan carga ni todos los CRUD con escritura. La cuenta `verificador.aws` se conserva inactiva. |
| HTTPS | Disponible | [Simulación de renovación](despliegue/evidencias/renovacion-certificado.txt). Certificado de la IP nueva y renovación programada. |

## Pendientes que impiden dar el paquete por cerrado

1. Investigar y corregir REN-EXP-01; repetir exportación de 10.000 registros con concurrencia y conservar corrección, versión y regresión.
2. Completar la carga normal de diez minutos y los escalones autorizados; registrar la mezcla requerida y los límites acordados. Repetir en la cuenta personal si es el entorno definitivo de evaluación.
3. Completar o justificar expresamente la exclusión de cálculos de metas y semáforos, con cálculos de control independientes cuando el motor forme parte del alcance.
4. Ensayar instalación desde clon limpio y reversión de versión; documentar restauración y recuperación del entorno definitivo según el alcance acordado.
5. Vincular fichas y resultados en una matriz HU → requisito → tarea/commit → prueba → resultado → responsable → evidencia. Diferenciar casos diseñados, ejecutados, aprobados, fallidos, bloqueados y no ejecutados; no sumar solicitudes HTTP y comprobaciones como si fueran casos equivalentes.
6. Identificar responsable real, fecha y decisión de aceptación. La aprobación del docente o responsable no se infiere de estos archivos.

## Organización

Los diagramas se encuentran en [UML](../uml/README.md). Los documentos internos anteriores se trasladaron a una carpeta secundaria conservando su contenido y su historial. Los enlaces de esta revisión apuntan a las nuevas ubicaciones; las rutas escritas dentro de documentos históricos describen la ejecución original.

No se modificó código, no se ejecutaron pruebas de carga adicionales ni se cambió AWS durante esta reorganización documental.
