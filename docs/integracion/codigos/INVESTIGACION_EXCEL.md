# Investigación de códigos del Excel — 20/10/2026

Fuente: `Copia INACAP 3ER COMPAÑIAS MATRIZ SGR TRIMESTRE 2026 REV.xlsx`. Lectura de fórmulas y columnas auxiliares; no se modificó el libro ni se importaron personas.

## Códigos operativos

La mayoría de las planillas concatena **prefijo del área + mes + día + número de fila operativo**. La fecha auxiliar referencia la fecha de la columna B; el número referencia la columna A. No incluye año, separadores ni relleno de ceros.

| Hoja | Celda del código | Fórmula | Componentes |
| --- | --- | --- | --- |
| AP ADM. | Q16 | `=CONCATENATE(M16:P16)` | M16=APA; N16=mes; O16=día; P16=A16 |
| COOR DISERCO | P20 | `=CONCATENATE(L20:O20)` | L20=COS; M20=mes; N20=día; O20=A20 |
| T OC1 | P18 | `=CONCATENATE(L18:O18)` | COM1 + mes + día + A18 |
| T OC 2–4 | P17 | `=CONCATENATE(L17:O17)` | COM2 / COM3 / COM4 + mes + día + A17 |
| G SOC 1 | AI21 | `=CONCATENATE(AE21:AH21)` | SOC + mes + día + A21 |
| G SOC2 | AI16 | `=CONCATENATE(AE16:AH16)` | SOC2 + mes + día + A16 |
| G SOC3 | AI16 | `=CONCATENATE(AE16:AH16)` | SCO3 + mes + día + A16 |
| G SOC4 | AG16 | `=CONCATENATE(AC16:AF16)` | SCO4 + mes + día + A16 |
| G SOC5 (hoja con espacio inicial) | AG16 | `=CONCATENATE(AC16:AF16)` | SOC5 + mes + día + A16 |
| PLAN y CON | O16 | `=CONCATENATE(K16:N16)` | PYG + mes + día + A16 |
| GES SEG | P17 | `=CONCATENATE(L17:O17)` | SEG + mes + día + A17 |

El orden SOC/SCO aparece así en el archivo; no se corrige como supuesto error. La presencia de GES SEG documenta la fórmula existente, sin añadir esa área a las doce configuradas.

Ejemplo ficticio calculado con la regla del libro: APA, mes 10, día 20 y número 1 → `APA10201`. No es un código extraído de una persona o registro real.

## Reclamos y tubo

En RECLAMOS, T10 concatena O10:S10: **área + día + mes + año + número**. Las celdas auxiliares P, Q, R toman DAY, MONTH y YEAR de N; S referencia B10. Es un orden distinto de las planillas operativas.

TUBO tiene el encabezado N2 «CODIGO VERIFICACION FOTO». No se encontraron fórmulas en las primeras cincuenta filas bajo ese encabezado; no se deduce que exista una regla automática propia. El código corresponde a un respaldo/origen y no debe reemplazarse por un identificador nuevo sin conservar ese vínculo.

## Catálogos y situación del sistema

El libro no proporciona un algoritmo para los códigos de delegaciones, cargos, ítems, tipos, subatenciones o períodos. Cualquier prefijo/consecutivo para estos catálogos será una decisión técnica del sistema, no una regla municipal atribuible al Excel.

Actualmente la interfaz pide código al crear esos seis catálogos. Actividades y compromisos ya tienen identificadores UUID automáticos y las atenciones tienen folio automático. El formulario del tubo permite escribir el código de verificación de foto y el de atención permite escribir el código de caso social para continuidad. La recuperación de contraseña requiere introducir el código recibido y debe conservar ese paso de verificación.

## Criterios para la implementación

- Autogenerar identificadores de nuevos catálogos en el servidor, manteniendo visibles y sin reescribir los existentes.
- Generar códigos operativos legibles con área, fecha y una secuencia persistente; conservar el identificador técnico y los vínculos originales.
- No copiar literalmente un número de fila como secuencia de base de datos. El formato del libro sin separadores puede ser ambiguo entre mes/día/número y se repite entre años o delegaciones.
- Una adaptación como `APA-20261020-000001` es una propuesta técnica que evita ambigüedades; no es el formato literal del Excel.
- Generar un nuevo caso social al elegir esa opción y seleccionar el caso existente al continuar; no generar uno distinto en cada gestión.
- Asociar el código de respaldo del tubo al origen correspondiente cuando se integre el flujo de atención/actividad → compromiso.

Este documento registra investigación y criterios; no declara implementada ni desplegada la automatización de códigos.
