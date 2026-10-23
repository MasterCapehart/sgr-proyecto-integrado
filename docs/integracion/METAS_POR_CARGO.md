# Metas por cargo, ítem y período

Incremento implementado y probado en local. No implica carga de metas reales ni despliegue en AWS.

En **Administración → Configuración de metas**, cada configuración puede indicar un cargo. Si se deja vacío, es una meta general. Para cada funcionario e ítem se usa primero la configuración activa de su cargo; si no existe, se utiliza la general. Nunca se suman ambas ni se aplican metas de otro cargo.

La combinación de ítem, período y cargo no se puede duplicar. Las configuraciones anteriores siguen siendo generales; las filas históricas sin calendario se conservan. La conciliación histórica no mezcla cargos.

Los cálculos individuales usan la meta y ponderación seleccionadas. Si ya estaba configurado el prorrateo de ese ítem por ausencias, se conserva al pasar de una meta general a una específica. El cierre conserva el cargo de la meta y sus valores, y no se reconstruye con el cargo actual.

El colectivo suma las metas ajustadas y los aportes limitados de cada persona. Cuando un ítem tiene ponderaciones distintas entre personas, sus porcentajes permanecen visibles; no se calcula un índice global con pesos inventados.

## Excel y carga pendiente

La matriz de origen contiene diferencias por cargo, por ejemplo la meta de conformación de organizaciones para Territorial 1 y Territorial 3. Este incremento permite representarlas sin duplicar el catálogo de ítems.

La carga se mantiene pendiente de confirmar asignaciones de personas, período, calendarios, metas dinámicas de emergencias y ponderaciones incompletas. No se han incorporado valores supuestos a producción.
