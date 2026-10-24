# Porcentaje de compromisos completados

Implementado y verificado en local. No desplegado en AWS por este incremento. Sin migraciones ni cambios de datos productivos.

## Uso y alcance

En Tubo de trabajo aparece «Compromisos completados», porcentaje, barra y cantidad realizada/total. El componente también funciona al consultar compromisos en Reportes operativos.

Fórmula: **compromisos distintos en estado Realizado / total de compromisos distintos ×100**. Ejemplo CAL-C:8 realizados,1 pendiente y1 en proceso →80 %,2 por completar. Ingresado también permanece en el denominador.

Se calcula sobre el mismo conjunto autorizado y filtrado del listado, antes de paginar. Por ello, filtrar únicamente Realizado produce100 %; filtrar Pendiente produce0 %. La pantalla indica expresamente que depende de los filtros actuales y permisos, incluyendo todas las páginas. No es un indicador fijo trimestral.

Sin compromisos, porcentaje nulo y texto «Sin compromisos»; no se interpreta como0 % ni100 %. Con compromisos pendientes pero ninguno realizado sí muestra0 %. Se conserva precisión decimal y se muestran hasta dos decimales con formato español. No se aplica umbral80 %, ponderación, puntaje ni tope120 a este indicador operativo.

La barra tiene nombre accesible y descripción realizada/total. La consulta se actualiza con el mecanismo de carga existente después del seguimiento, cambios de estado o filtros. Las otras tarjetas permanecen con su comportamiento anterior.

## Fuente y verificación

Plan de pruebas de segunda evaluación, B3, CAL-C, página7. Fórmula del Excel TUBO!V3 y concepto de agenda de la presentación original, diap14. No incorpora automáticamente el componente porcentual al puntaje integral ni completa su pauta.

23 pruebas relacionadas correctas, con5 específicas de porcentaje, neutralidad, estados/filtros, redondeo/actualización y privacidad de persona/delegación. [Resultado local](pruebas-locales.txt). Se actualizó la prueba de contraste CAL-C para exigir80 % en la respuesta.

Edge local:8/10=80 %, barra accesible, filtros, estado vacío y móvil sin desbordamiento ni errores JavaScript. Datos ficticios únicamente en SQLite local y base de pruebas temporal. Revisión independiente sin defectos concretos.
