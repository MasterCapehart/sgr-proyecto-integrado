# DA05 · Estados y etiquetas del nuevo flujo

Tabla de referencia para que las pantallas, reportes y textos usen los mismos nombres que el documento **Requerimientos Complementarios SGR** (en adelante, RC). Solo documenta nombres y significados: no implementa lógica ni define colores.

## 1. Tres flujos distintos

| Flujo | Qué sigue | Quién lo cambia | Fuente |
|---|---|---|---|
| **Verificación** de la actividad | Si la actividad es válida y si suma a la meta | El verificador | RC §7, págs. 5–6 |
| **Seguimiento** en el Tubo | Si la solicitud o gestión fue atendida y cerrada | El responsable del registro | RC §8, pág. 6 |
| **Tubo de cartas** | El trámite de una carta recibida | El responsable de seguimiento | RC §8, pág. 6 |

**Regla clave:** son flujos independientes. Aprobar una evidencia o una actividad **no** cierra un registro del Tubo, y cerrar un registro del Tubo **no** aprueba la actividad ni la hace ponderar.

## 2. Estados de verificación (seis)

| Estado (nombre del RC) | Significado | ¿Suma a la meta? |
|---|---|---|
| Pendiente | La actividad fue enviada y aún no ha sido revisada. | No |
| Aprobada y pondera | La actividad es válida y se incluye en el cálculo de la meta. | **Sí** |
| Aprobada y no pondera | La actividad queda registrada, pero no incrementa el indicador. | No |
| Solicitud de antecedentes | El funcionario debe complementar información o evidencias. | No (hasta nueva revisión) |
| Rechazada | El registro no cumple las condiciones definidas. | No |
| Anulada | El registro se conserva por trazabilidad, pero queda sin efecto. | No |

Fuente: RC §7, "Estados de verificación", págs. 5–6. El dashboard solo usa actividades **Aprobada y pondera** (RC §13).

## 3. Estados del Tubo (seis)

| Estado (nombre del RC) | Significado | Cómo se asigna |
|---|---|---|
| Pendiente | Registrado en el Tubo, sin avance. | Manual |
| En proceso | El responsable está trabajando en él. | Manual |
| Realizado | La acción comprometida se ejecutó. | Manual |
| Cerrado | El seguimiento terminó, con resultado y fecha de cierre registrados. | Manual |
| No aplica | El registro no corresponde ser atendido; se conserva con motivo. | Manual |
| Vencido | La fecha de compromiso expiró sin cierre. | **Calculado** por el sistema |

Fuente: RC §8, "Estados en el Tubo", pág. 6.

## 4. Estados del Tubo de cartas (seis)

| Estado (nombre del RC) |
|---|
| Ingresada |
| Derivada |
| En proceso |
| Aprobada |
| Finalizada |
| No aplica |

Fuente: RC §8, "Tubo de cartas", pág. 6. El RC no define el significado de cada estado; queda por precisar en la tarea correspondiente. Ojo: "Aprobada" de cartas no es lo mismo que "Aprobada y pondera" de verificación.

## 5. Diferencias que no deben confundirse

| Término | Flujo | Qué significa | Qué NO significa |
|---|---|---|---|
| **Aprobada y pondera** | Verificación | El verificador aceptó la actividad y la cuenta para la meta. | No significa que el compromiso del Tubo esté realizado o cerrado. |
| **Realizado** | Tubo | El responsable ejecutó la acción comprometida. | No significa que se cerró el seguimiento ni que la actividad pondere. |
| **Cerrado** | Tubo | El seguimiento terminó y se registró resultado y fecha de cierre. | No significa que la actividad fue aprobada ni que pondera. |
| **Aprobada** (evidencia) | Revisión de archivo | El archivo de respaldo es válido. | No equivale a "Aprobada y pondera" de la actividad (DF10). |

Un compromiso puede estar **Realizado** y aún no **Cerrado**. Una actividad puede estar **Aprobada y no pondera** con su compromiso **Cerrado**.

## 6. Correspondencia con lo que muestra hoy el sistema

Observado en el recorrido de DA01 (AWS, 06-11-2026). Los cambios los resuelven las tareas indicadas; esta tabla solo documenta la diferencia.

| Hoy en el sistema | Pantalla | Nombre en el RC | Tarea que lo resuelve |
|---|---|---|---|
| Borrador | Planilla | Sin equivalente (estado previo al envío) | DF10, DF13 |
| Pendiente | Planilla | Pendiente | — |
| Validada | Planilla | Aprobada y pondera **o** Aprobada y no pondera (falta la decisión explícita) | DF10, DF11 |
| Corrección | Planilla y evidencias | Solicitud de antecedentes | DF11, DF12 |
| Rechazada | Planilla y evidencias | Rechazada | — |
| Anulada | Evidencias | Anulada | — |
| Ingresado | Tubo | Sin equivalente directo (el RC parte en Pendiente) | DF23 |
| Pendiente, En proceso, Realizado | Tubo | Iguales | — |
| (no existe) | Tubo | Cerrado, No aplica, Vencido | DF23 |
| (no existe) | — | Estados del Tubo de cartas | Tarea del Tubo de cartas |

## 7. Colores

**No se asignan colores definitivos.** El semáforo del dashboard usa verde, amarillo y rojo según rangos aún por confirmar (decisión D01: umbrales y color amarillo o naranjo; RC §13, pág. 9). Mientras no se confirme:

- No usar el color como único indicador del estado: mostrar siempre el nombre.
- No reutilizar los colores del semáforo para estados de verificación o del Tubo, para no confundir "en riesgo" con "pendiente".

## 8. Otros estados mencionados en el RC (referencia)

| Elemento | Estados | Fuente |
|---|---|---|
| Evidencias (indicador del dashboard) | Pendientes, aprobadas, rechazadas, con solicitud de antecedentes | RC §13, pág. 9 |
| Hitos | Planificados, próximos, en ejecución, finalizados, vencidos, cancelados | RC §13, pág. 9 |
