# Excel de referencia para la adaptación del SGR

Fecha de revisión: 16-10-2026, America/Santiago.

## Decisión solicitada por Daniel Flores

El sistema debe resultar familiar para las personas que trabajan con la matriz actual. Este archivo pasa a ser la referencia principal para vocabulario, campos, orden de columnas, etapas de trabajo, listas y estructura de consulta de las pantallas operativas. Los requisitos de la segunda evaluación siguen definiendo acceso, recuperación, roles, delegaciones, validaciones y evidencias. No se eliminan funciones obligatorias por no estar representadas en Excel.

Fuente de solo lectura: `Copia INACAP 3ER COMPAÑIAS MATRIZ SGR TRIMESTRE 2026 REV.xlsx`, en la carpeta padre del proyecto.
SHA-256: `65d2f3616fb547491a42b7823159a08e9d8cff09db531074c47f331a682beb05`.

La adaptación posterior está documentada en [Informe de implementación](adaptacion-local/Informe_Adaptacion.md). Este documento conserva la lectura y las brechas identificadas al recibir la fuente.

## Estructura observada

21 hojas: 18 visibles y 3 ocultas. Las dimensiones de las hojas incluyen celdas formateadas y no equivalen al número de atenciones. Se identificaron 49.226 celdas con fórmulas; no se verificó su corrección matemática ni se recalculó el archivo fuente con Excel.

| Hojas reales | Correspondencia de pantalla propuesta | Estado actual |
|---|---|---|
| TUBO | Tubo de trabajo, con columnas y estados de la planilla | Adaptada: unidad por registro, referencia de foto, rótulos y exportación; los cálculos continúan aplazados |
| AP ADM., COOR DISERCO, T OC1, T OC 2, T OC 3, T OC 4, PLAN y CON, GES SEG | Mi planilla de trabajo, con vista por función/cargo autorizado | Vistas de columnas por función y cargo con planilla elegible; se conservan campos auxiliares de cálculo fuera del formulario |
| G SOC 1, G SOC2, G SOC3, G SOC4, espacio inicial + G SOC5 | Gestión social: listado familiar y ficha por caso con tres etapas | Tres etapas, fechas separadas y vínculo al tubo implementados; fecha heredada conservada sin reinterpretación |
| RECLAMOS | Reclamos y felicitaciones, respetando ambos bloques | Captura, consulta, edición versionada, filtros y exportación persistentes implementados |
| SALON | Vista de ponderaciones, comisiones, metas y avances | No hay reproducción integral; cálculo de desempeño sigue aplazado |
| SEMAFORO | Resumen por área/responsable y tiempos del período | Vista de aviso de cálculo aplazado; no hay semáforo operativo completo |
| RESUMEN | Resumen de avances, últimos ingresos y seguimiento | Reportes actuales de registros; no reproduce aún toda esta hoja |
| CARTAS (oculta) | Correspondencia, si se confirma que se utiliza | No activar como módulo obligatorio por su sola presencia en una hoja oculta |
| LISTA, DATO MENU (ocultas) | Apoyo para listas/opciones, sin pantalla de trabajo independiente por defecto | Revisar listas y dependencias antes de cualquier importación |

La expansión de abreviaturas como AP ADM., T OC y PLAN y CON debe confirmarse con quienes utilizan el archivo; mantener los nombres originales como referencia hasta entonces. Las hojas numeradas no justifican crear una tabla de base de datos o un permiso diferente por número: debe validarse si representan personas, funciones o distribuciones de trabajo.

## Detalles que no debe perder la adaptación

### Tubo de trabajo

Fuente `TUBO!A2:N2`: N°, fecha solicitud, actividad/solicitud/problema, INT/EXT, solicitante, territorio, responsable, fecha de compromiso, mes compromiso, área/persona de apoyo, avance/observaciones, estatus, unidad y código de verificación de foto.

Las opciones del estatus incluyen INGRESADO, EN PROCESO, PENDIENTE y REALIZADO. Los valores de selección inicial, por ejemplo ESTATUS, no se consideran estados de negocio. El nombre «Tubo de trabajo» debe ser visible; «Agenda y compromisos» puede conservarse como explicación secundaria.

### Planilla por función

Ejemplo `T OC1!A17:T17`: N°, fecha, actividad/solicitud/problema, acción, contacto, fono, ingreso a tubo, ítem, unidad, auxiliares de fecha/área/mes/día/número, código foto, imagen verificadora, verificador válido y resultado. Hay columnas ocultas y auxiliares; no todas deben solicitarse como datos manuales.

Las listas de ítems y las columnas no son idénticas entre funciones. El componente de tabla debe admitir esquemas por función sin mezclar su cargo con el rol de permisos. La exportación debe conservar la correspondencia y el orden de la plantilla elegida.

### Gestión social

Fuente principal `G SOC 1!A20:AO20` y `G SOC2!A15:AO15`. Se distinguen fecha de ingreso, tipo/subatención, usuario ciudadano, RUT, teléfono, requiere visita, ingreso al tubo, primera gestión, fecha programada de visita, observaciones, segunda gestión, fecha de visita realizada, fecha de informe, tercera gestión, fecha de beneficio, código, imagen/verificador, resultado y devoluciones.

Brecha inicial resuelta en las migraciones aditivas: se separaron fechas programada y realizada y se añadió tipo de gestión por etapa. El campo `fecha_visita` previo permanece como fecha heredada sin clasificación; no se convirtió automáticamente en una de las fechas nuevas.

Existen diferencias de orden entre G SOC3 y las demás hojas. Cualquier importación futura debe mapear por esquema verificado de hoja y etiqueta, no asumir que la tercera gestión siempre está en la misma columna.

### Reclamos y felicitaciones

`RECLAMOS!C9:W9` y `C23:W23` tienen bloques diferentes: situación reclamada o felicitada, usuario, contacto, ubicación, profesional involucrado, medio escrito y datos de información/seguimiento. El puntaje y resultado pertenecen al cálculo aplazado; la captura operativa deberá diseñarse separadamente si se incluye el módulo.

## Diseño de interacción propuesto

- Mantener el rojo municipal, Arial y contexto permanente; usar los nombres de planilla que reconoce el funcionario.
- Entrar directamente al listado de trabajo correspondiente al cargo y delegación autorizados, con período y funcionario visibles.
- Orden y encabezados familiares, columnas clave fijas, desplazamiento horizontal dentro de la tabla y filtros simples.
- Vista principal de trabajo y detalle lateral o formulario para capturar/editar; los campos calculados no se mezclan con los editables.
- Los KPI acompañan el trabajo; no desplazan el formulario ni se presentan como el resultado ponderado del Excel.
- Revisiones y devoluciones ligadas al registro original y al archivo; conservar auditoría y control de cambios concurrentes.
- No crear 21 entradas de menú ni una base/tabla por cada hoja. Ofrecer vistas por función y pestañas por flujo.

## Integridad de la fuente y alcance

El archivo fuente no se editó, exportó ni importó a la base de datos. Las capturas de cabeceras se conservan localmente sin filas de ciudadanos. No se deben copiar datos personales, nombres de ejemplo de listas de responsables ni valores de selección inicial como catálogos institucionales aprobados.

Se encontró al menos una fórmula con referencia explícitamente rota: `SALON!F928` contiene `#REF!`. El renderizador también advierte limitaciones con algunas referencias y nombres; sus advertencias no se consideran por sí solas errores del Excel. No se sustituyen resultados almacenados por los del renderizador ni se afirma equivalencia matemática.

AWS, publicación en GitHub y el motor de cálculos de desempeño siguen aplazados. La correspondencia se implementó en el incremento descrito en el informe enlazado. El motor ponderado y la importación de filas históricas permanecen fuera de esta adaptación.
