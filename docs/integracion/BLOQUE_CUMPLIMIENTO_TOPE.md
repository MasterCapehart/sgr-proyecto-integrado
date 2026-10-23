# Cumplimiento validado y tope del 120 % — R10

Estado: implementado y verificado en local el 22/10/2026. Sin despliegue AWS. Sin nuevas migraciones.

## Base y decisiones

Se mantiene la estructura del Excel: avance/meta y aplicación de ponderación. El límite del sistema es el nuevo requerimiento del 120 % por funcionario, ítem y período, usando la meta ajustada exacta. Sustituye la nota histórica del 150 % por colaborador de RECLAMOS!B6; el libro no contiene una fórmula MIN que implemente ese límite.

No se suman aportes entre personas, ítems o delegaciones. Los indicadores colectivos siguen fuera de este bloque. La configuración actual expresa la ponderación como porcentaje: 20 significa 20 %. Por ejemplo, 120 % de cumplimiento con peso 20 % aporta 24 puntos porcentuales al cumplimiento ponderado del ítem. No se inventan pesos, bonos ni fórmulas de felicitaciones o tubo de trabajo.

## Qué aporta

Una actividad aporta una unidad cuando conserva candidatura explícita en su snapshot, está Validada y todos sus respaldos vigentes no anulados están Aprobados, con revisión de la misma versión por otra persona. Varias evidencias no duplican una actividad. No se presume candidatura ni aprobación para historiales sin esas constancias. No se reinterpretan retrospectivamente las reglas capturadas.

Coordinación, Otra gestión, datos faltantes, tardíos y demás exclusiones capturadas no aportan; tampoco los borradores, pendientes o respaldos no aprobados. El detalle explica los motivos.

**Reconocido = mínimo entre unidades válidas y meta ajustada exacta × 1,20.**

**Cumplimiento = mínimo(120 %, reconocido/meta ajustada × 100).**

**Aporte ponderado = cumplimiento × ponderación / 100.**

El orden de asignación es fecha de realización, creación y PK. Meta 10 con 13 válidas reconoce 12 y conserva 13. Meta 10,5 con 13 válidas reconoce 12,6: la actividad del cruce aporta 0,6 al cálculo, pero sigue siendo una actividad completa registrada. Se conserva precisión decimal y se muestran hasta dos decimales con coma, sin ceros innecesarios.

Sin calendario, sin meta evaluable, meta cero o sin días disponibles no se calcula cumplimiento ni ponderado; se informa un estado neutral. Esto también se aplica a una meta no proporcional con calendario sin jornada o ausencia total.

## Semáforo

La estructura proviene de SEMAFORO!N4 y del factor 0,60 de L3. El objetivo al día se adapta al calendario laboral explícito del sistema: días disponibles transcurridos/días disponibles del período, limitado al 100 %. Descuenta ausencias y fechas no laborables.

- Verde: cumplimiento del ítem igual o superior al objetivo al día.
- Naranjo: desde el 60 % de ese objetivo.
- Rojo: por debajo.
- Sin jornada transcurrida/disponible o sin exigibilidad: neutral.

No se copia una extrapolación del objetivo fuera del período ni se usa el 80 % como umbral fijo en lugar de esta fórmula. La pantalla muestra el criterio y el objetivo aplicado. Este componente no certifica por sí solo una evaluación integral del desempeño.

## Historia, concurrencia y permisos

El cálculo se integra en el resumen autorizado de ausencias: propio para funcionario; equipo autorizado para administrador/delegado. Los detalles incluyen códigos, fechas, estado, aporte y motivo, sin nombres de vecinos ni contactos. Se muestran hasta 50 registros de detalle y se cuentan todos.

El cierre conserva este resultado dentro del snapshot privado de disponibilidad. Los períodos cerrados sin cálculo de este bloque no reciben resultados retrospectivos inferidos. Si se corrigen estados operativos después del cierre, el snapshot no cambia; una reapertura autorizada permite recalcular.

Revisión y anulación de evidencias bloquean primero los períodos que contienen la fecha, después actividad y evidencia, igual que el orden del cierre. Una prueba concurrente verifica que una aprobación que espera al cierre no modifica el resultado congelado. No se cambia el cupo diario: los registros posteriores al tope siguen permitidos, sujetos a las siete candidaturas por día ya vigentes.

## Verificación

- 61 pruebas de cumplimiento, ausencias, períodos y cierre correctas.
- 538 pruebas de regresión correctas, con un fallo esperado preexistente.
- Pruebas rojas/verdes del tope, cruce fraccionario, exclusiones, revisión real, autocontrol, privacidad/ámbito, cierre concurrente y disponibilidad cero.
- Navegador local: 13 registros con aprobación mediante el flujo real (7 hoy y 6 ayer), reconoce 12/120 %; meta 10,5 reconoce 12,6 y cruce 0,6; vista móvil y consulta propia sin gestión.
- Revisión independiente detectó el caso de meta no prorrateable sin disponibilidad; corregido y cubierto con prueba roja/verde.
- Sin cambios pendientes de modelos/migraciones ni errores de sintaxis JS o espacios del diff.

Solo datos ficticios en SQLite local y base temporal de pruebas. Sin modificaciones al Excel, diagramas, producción ni repositorio remoto.
