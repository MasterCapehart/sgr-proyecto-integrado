# DA07 · Leyendas y ayudas del dashboard

Textos de ayuda para las tarjetas y paneles del dashboard (RC §13 y §14, págs. 8–9). Cada texto dice **qué cuenta** y **qué no cuenta**, para que no se confundan cifras de distinto significado.

**Reglas de estos textos**

- No contienen cifras fijas: los valores se muestran con campos entre llaves, por ejemplo `{trimestre}`, que el sistema reemplaza.
- No definen umbrales ni colores del semáforo: se remiten a los "rangos definidos" (decisión D01, pendiente).
- No inventan puntajes: el cumplimiento solo usa actividades **Aprobada y pondera** (RC §13).
- Los nombres de estados son los de DA05.

---

## 1. Textos comunes a todo el dashboard

| Elemento | Texto |
|---|---|
| Última actualización | Actualizado el {fecha} a las {hora}. Las cifras corresponden a ese momento. |
| Contexto de los filtros | Mostrando {vista} · {delegación} · {trimestre}. Cambia los filtros para ver otro período o persona, según tus permisos. |
| Sin datos (general) | Aún no hay registros para este filtro. Cuando se registren y revisen actividades, aparecerán aquí. |
| Sin metas asignadas | No hay metas asignadas a esta persona en {trimestre}, por lo que no se puede calcular el cumplimiento. |
| Sin calendario | No hay calendario laboral configurado para {trimestre}; el avance esperado no se puede calcular. |
| Cobertura parcial | Algunas personas o metas no tienen datos suficientes. No se cuentan como cero ni se incluyen en el promedio. |
| Error de carga | No se pudieron cargar los datos. Intenta de nuevo en unos minutos. |
| Ir al detalle | Ver registros que originan esta cifra. |

## 2. Diferencia clave: registradas frente a aprobadas que ponderan

Texto para mostrar junto a las cifras de actividades (tooltip o nota al pie):

> **Registradas** son todas las actividades que ingresaste, en cualquier estado. **Aprobadas que ponderan** son solo las que el verificador aprobó y marcó como válidas para tu meta. El cumplimiento se calcula únicamente con estas últimas.

## 3. Vista Funcionario

| Tarjeta o panel | Texto de ayuda | Cuenta | No cuenta |
|---|---|---|---|
| Metas | Metas asignadas a ti en {trimestre}, con su cantidad objetivo y ponderación. | Metas activas del trimestre. | Metas de otros trimestres o inactivas. |
| Objetivo esperado | Cantidad que deberías llevar a la fecha según tu meta y tus días trabajados. | Días laborales transcurridos, descontando ausencias registradas. | Días no laborables ni ausencias aprobadas. |
| Resultado real | Actividades aprobadas que ponderan para esta meta. | Solo estado **Aprobada y pondera**. | Pendientes, aprobadas que no ponderan, rechazadas, anuladas y con solicitud de antecedentes. |
| Cumplimiento | Resultado real dividido por la cantidad objetivo. Se muestra hasta un máximo de 120 % por meta. | Actividades aprobadas que ponderan. | Lo que supera el 120 %: se sigue registrando, pero no aumenta el indicador. |
| Ponderación obtenida | Cumplimiento aplicable multiplicado por la ponderación de cada meta. | Metas con cumplimiento calculado. | Metas sin datos (se muestran como "Sin evaluación", no como cero). |
| Semáforo | Clasificación de tu avance según los rangos definidos por la institución. | Avance frente al objetivo esperado a la fecha. | No es una calificación final ni una evaluación de desempeño. |
| Actividades | Total de actividades que registraste en {trimestre}, separadas por estado de verificación. | Todos los estados. | — (es un conteo, no un resultado). |
| Evidencias pendientes | Respaldos que enviaste y que aún esperan revisión de otra persona. | Evidencias vigentes en estado Pendiente. | Evidencias anuladas o reemplazadas. |
| Solicitudes por estado | Registros del Tubo a tu cargo, por estado. | Pendiente, En proceso, Realizado, Cerrado, No aplica y Vencido. | Registros de otras personas. |
| Vencimientos | Compromisos a tu cargo con fecha vencida o próxima a vencer sin cierre. | Registros sin Cerrado ni No aplica. | Registros cerrados aunque se hayan cerrado tarde. |
| Último registro | Fecha de tu actividad registrada más reciente. | Cualquier actividad propia. | Ediciones o revisiones. |
| Promedio diario | Actividades registradas dividido por días trabajados del período. | Días laborales transcurridos. | Ausencias y días no laborables. Es un dato de ritmo, no de cumplimiento. |
| Reclamos y felicitaciones | Registros donde figuras como profesional involucrado. | Ambos tipos, por separado. | No suman ni restan al cumplimiento. |

## 4. Vista Delegación

| Tarjeta o panel | Texto de ayuda | Cuenta | No cuenta |
|---|---|---|---|
| Resultados por funcionario | Cumplimiento de cada persona de la delegación en {trimestre}. | Personas con metas y calendario. | Personas sin evaluación (se listan aparte). |
| Resultado del equipo | Cumplimiento conjunto de la delegación según las metas de su equipo. | Personas con evaluación. | Personas sin evaluación: no se cuentan como cero. |
| Solicitudes por estado | Registros del Tubo de la delegación, por estado. | Todos los responsables. | Otras delegaciones. |
| Distribución por territorio y responsable | Cantidad de registros por territorio y por persona responsable. | Registros con territorio informado. | Es una distribución, no un porcentaje de cumplimiento. |
| Hitos próximos | Hitos de la delegación con fecha de inicio cercana. | Hitos planificados o próximos. | Hitos finalizados o cancelados. |
| Metas de menor cumplimiento | Metas con el cumplimiento más bajo de la delegación en {trimestre}. | Metas con cumplimiento calculado. | Metas sin evaluación. |
| Evolución trimestral | Cumplimiento esperado y real semana a semana durante {trimestre}. | Actividades aprobadas que ponderan, según la fecha de la actividad. | Actividades aprobadas después de cerrar el trimestre (salvo reapertura autorizada). |

## 5. Paneles de estado (RC §14)

| Panel | Texto de ayuda |
|---|---|
| Actividades por verificación | Actividades según la decisión del verificador: pendientes, aprobadas que ponderan, aprobadas que no ponderan, rechazadas y con solicitud de antecedentes. Solo las aprobadas que ponderan cuentan para la meta. |
| Estado del Tubo | Registros del Tubo según su seguimiento. "Realizado" significa que se ejecutó la acción; "Cerrado" que terminó el seguimiento. Ninguno de los dos aprueba la actividad. |
| Evidencias por estado | Respaldos según su revisión. Aprobar un archivo no equivale a que la actividad pondere. |
| Próximos vencimientos | Registros del Tubo con fecha de compromiso vencida o cercana, con su responsable. |
| Carga por funcionario | Registros del Tubo de cada persona, por estado. Muestra carga de trabajo, no desempeño. |

## 6. Pendiente de decidir (no lo define DA07)

- Rangos y colores del semáforo (D01).
- Qué cuenta como "próximo a vencer" y "hito próximo" (cantidad de días).
- Tratamiento de ausencias en el objetivo esperado (D03).
