# Metas territoriales — propuesta pendiente de definición

## Estado observado

R13 muestra distribución de actividades por `Actividad.sector`, agrupando espacios y mayúsculas; identifica registros sin territorio. El territorio es texto, no una asignación de metas. `collective.py` calcula cumplimiento por ítem desde resultados individuales y devuelve conteos territoriales por separado. No existe denominador territorial aprobado ni porcentaje territorial implementado. Los períodos cerrados no conservan dimensión territorial suficiente y no se reconstruyen desde datos actuales.

Esta propuesta documenta decisiones necesarias; no implementa modelos, valores, fórmulas nuevas ni cambios de producción. Tampoco certifica que una asignación individual por cargo represente una meta territorial compartida.

## Decisiones necesarias

| Tema | Decisión que debe aprobar negocio | Consecuencia para el diseño |
|---|---|---|
| Unidad territorial | Definir qué representa un territorio y su relación con delegación, sector, barrio u organización; escoger catálogo estable o texto normalizado. | Identificador histórico, alias y tratamiento de «sin territorio»; no fusionar territorios solo por similitud de nombres. |
| Unidad del indicador | Definir ítem, unidad contable, población cubierta y evidencia exigida. | No mezclar unidades diferentes ni inferir metas desde conteos de registros. |
| Responsabilidad | Definir quién asigna, revisa y modifica metas; equipo/personas responsables y vigencias. | Permisos explícitos y auditoría; no ampliar roles por analogía. |
| Meta compartida | Distinguir meta única del territorio de suma de metas individuales; resolver actividades con varias personas o territorios. | Un identificador de aporte y regla de atribución para evitar duplicar numerador o denominador. |
| Período | Definir calendario, fechas, cambios de asignación y corte histórico. | Conservar pertenencia territorial y meta al cierre; reapertura con versión y motivo. |
| Ausencias | Definir si una ausencia individual reduce una meta territorial compartida, si se redistribuye trabajo y cómo se evita descontar dos veces. | No aplicar automáticamente el prorrateo individual de R12 al denominador colectivo territorial. |
| Tope | Determinar si existe un tope territorial, su base y su interacción con el 120 % individual vigente. | Mantener separado aporte individual reconocido, actividad registrada y eventual reconocimiento territorial. No asumir otro porcentaje. |
| Fuente Excel | Identificar libro, versión, hoja, celda/rango, fórmula y responsable de aprobación para cada valor. | Fuente verificable y trazabilidad; notas históricas no equivalen a fórmula vigente. |
| Excepciones | Resolver meta cero, territorio nuevo, registro sin territorio, traslado y datos históricos insuficientes. | Estado sin evaluación cuando no hay base; no convertir ausencia de datos en incumplimiento. |
| Presentación | Definir si se requiere cumplimiento, cobertura, semáforo o distribución, y el alcance de consulta. | Etiquetas que distingan conteos de cumplimiento y visibilidad por delegación autorizada. |

## Criterios propuestos para una futura aceptación

1. Una meta compartida se cuenta una sola vez aunque tenga varias personas responsables; su unidad y período son explícitos.
2. Una actividad no se duplica al participar varias personas o al corregir una etiqueta territorial. La regla de atribución se aprueba antes del cálculo.
3. Toda modificación conserva actor, motivo, versión y fecha; el cierre preserva meta, territorio, asignación y regla de cálculo utilizados.
4. Los casos sin meta o sin dimensión territorial histórica muestran cobertura o estado sin evaluación; no inventan porcentajes.
5. Las pruebas cubren aislamiento entre delegaciones, acceso por los seis roles, ausencia parcial/total, cambio de responsables, duplicados y cierre/reapertura usando datos ficticios.
6. El resultado explica origen del numerador, denominador y reglas aprobadas. La distribución operativa actual sigue identificada como conteos hasta disponer de esa definición.

## Validación de negocio pendiente

No se dispone de definición aprobada de unidad territorial, meta compartida, atribución, impacto de ausencias, tope territorial ni fuente exacta de valores. El código actual no resuelve estas decisiones. La aprobación de esas reglas es condición previa a especificar e implementar el cálculo; este documento no solicita desplegar ni modificar bases de datos.
