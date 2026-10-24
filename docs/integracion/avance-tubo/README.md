# Porcentaje de compromisos completados

Implementado, verificado en local y desplegado en AWS el 23/10/2026. Versión `33fd14d9bb1ca654d7c6b69ab972b086f92ec94f`. Sin migraciones ni cambios de datos productivos.

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

## Verificación AWS

[Resultados](aws-verificacion.json). Salud y versión correctas. Administrador:1 compromiso autorizado y realizado →100 %. Funcionario:sin compromisos autorizados →estado neutral, sin barra ni porcentaje numérico. Se compararon los conteos contra todas las páginas de registros autorizados. Filtro sin resultados, vista móvil sin desbordamiento y ausencia de errores JavaScript comprobados para ambos perfiles.

Los compromisos consultados antes y después permanecen idénticos. No se guardaron compromisos de prueba ni se alteraron sus estados. La autenticación produce su auditoría normal. Sin migraciones nuevas; respaldo previo cifrado en S3 y servicios activos.

## Ajuste visual local posterior

A petición del usuario se redujo el tamaño del indicador, con porcentaje lateral, barra fina, texto breve y tarjetas secundarias compactas. Se añadió una hoja de estilos limitada al componente del tubo; las otras vistas mantienen sus indicadores previos. Se actualizó la referencia de caché en las seis páginas publicadas que consumen el componente.

Este ajuste visual está en local, pendiente de despliegue. No modifica cálculo ni datos. Vista comprobada en el navegador integrado con sesión de demostración iniciada y página del tubo abierta directamente. Para presentar futuras vistas locales, iniciar sesión mediante el acceso normal antes de entregar la página; no desactivar autenticación ni añadir un bypass.

## Variante de tarjeta única — vista local

El usuario eligió reunir todo el resumen en una sola tarjeta horizontal: total, porcentaje, realizados, por completar y vencidos, con barra fina. Se eliminan las cuatro tarjetas adicionales únicamente cuando existe el indicador del tubo; los demás módulos conservan sus tarjetas. Los vencidos son un subconjunto de los compromisos por completar, no una cantidad que deba sumarse al total.

La página local se mostró directamente con la sesión de demostración ya iniciada y resultado8/10=80 %. Sin cambios de cálculo ni datos. Esta variante reemplaza visualmente al ajuste compacto previo y permanece pendiente de desplegar.
