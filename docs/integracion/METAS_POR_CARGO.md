# Metas por cargo, ítem y período

Incremento implementado, probado en local y desplegado en AWS el 23/10/2026. Versión `6032f315ea000f6170b6ad9f3ca3b204aee6eb67`; migración 0028 aplicada. No implica carga de metas reales.

En **Administración → Configuración de metas**, cada configuración puede indicar un cargo. Si se deja vacío, es una meta general. Para cada funcionario e ítem se usa primero la configuración activa de su cargo; si no existe, se utiliza la general. Nunca se suman ambas ni se aplican metas de otro cargo.

La combinación de ítem, período y cargo no se puede duplicar. Las configuraciones anteriores siguen siendo generales; las filas históricas sin calendario se conservan. La conciliación histórica no mezcla cargos.

Los cálculos individuales usan la meta y ponderación seleccionadas. Si ya estaba configurado el prorrateo de ese ítem por ausencias, se conserva al pasar de una meta general a una específica. El cierre conserva el cargo de la meta y sus valores, y no se reconstruye con el cargo actual.

El colectivo suma las metas ajustadas y los aportes limitados de cada persona. Cuando un ítem tiene ponderaciones distintas entre personas, sus porcentajes permanecen visibles; no se calcula un índice global con pesos inventados.

## Excel y carga pendiente

La matriz de origen contiene diferencias por cargo, por ejemplo la meta de conformación de organizaciones para Territorial 1 y Territorial 3. Este incremento permite representarlas sin duplicar el catálogo de ítems.

La carga se mantiene pendiente de confirmar asignaciones de personas, período, calendarios, metas dinámicas de emergencias y ponderaciones incompletas. No se han incorporado valores supuestos a producción.

## Verificación del despliegue

Respaldo de datos cifrado y archivos anteriores conservados antes de migrar. Salud, versión y hashes de archivos correctos; servicios activos. Formulario con cargo opcional verificado en escritorio y móvil sin errores de JavaScript. Las configuraciones consultadas permanecieron sin cambios; no se guardaron metas durante esta comprobación.

Pruebas locales: 568 ejecutadas, resultado correcto con un fallo esperado preexistente.

## Carga de la pauta de referencia — 23/10/2026

Por autorización del usuario, se cargaron en AWS 49 configuraciones de meta fija para los 12 cargos del Excel. Período histórico: **Julio–septiembre 2026 · referencia Excel**, del 01/07/2026 al 30/09/2026 (id 4). No se trasladaron las cantidades a otro trimestre.

Se verificaron por lectura las 49 combinaciones de ítem/cargo/período, sus cantidades y ponderaciones. Las cuentas, metas y períodos preexistentes permanecieron sin cambios. `funcionario.aws` conserva su cargo de demostración. Se reutilizó el ítem existente de atención telefónica/presencial (código ITEM-001), verificando nombre y asociaciones de cargo para no duplicarlo.

Se conservan pendientes las metas dinámicas de emergencias y los componentes separados de tubo, felicitaciones y reclamos. Las dos metas fijas de Planificación conservan sus valores de origen (12/peso15 y 8/peso30); la pauta principal incompleta no se considera aprobada por esta carga ni se completa con valores inventados. No se configuraron calendarios ni se asignaron metas a personas.

Esta operación fue una carga de datos mediante la API con auditoría normal, sin nueva versión de aplicación. Fuente SHA-256: `65d2f3616fb547491a42b7823159a08e9d8cff09db531074c47f331a682beb05`.
