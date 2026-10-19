# Adaptación operativa al Excel — plan de implementación

**Objetivo:** conservar vocabulario, campos y flujos de la matriz sin importar nombres ficticios ni filas personales.
**Arquitectura:** ampliar modelos y API existentes con migraciones aditivas; esquemas de planilla por función; componentes comunes para navegación, tablas y formularios. Mantener Django/MySQL, HTML/JS/CSS y SweetAlert2.
**Referencia aprobada:** docs/revision-local/excel/Referencia_Operativa_Excel.md; usuario confirma adaptar lo demás excluyendo nombres ficticios.
**Restricciones:** solo sgr-eva2-local; sin commits/remotos/AWS; sin motor ponderado; no importar trabajadores ni ciudadanos del archivo; no reinterpretar fecha histórica ambigua.

- [x] Social: pruebas RED/verde de fechas separadas, tipo de gestión por etapa, vínculo autorizado al tubo y preservación de fecha heredada. Ampliar modelos, validación, ficha y exportación.
- [x] Tubo: unidad y referencia de foto, validación/versiones, listado y exportación con columnas verificadas.
- [x] Planillas por función: perfiles declarativos de las seis familias, cargo con plantilla elegible y captura auditada del perfil; listas de ítems de referencia sin responsables; selector y tabla por perfil, sin elevar permisos.
- [x] Reclamos/felicitaciones: captura y consulta persistentes, edición versionada, búsqueda/exportación y scope propio/equipo con permisos específicos. Conservar archivos mediante vínculo autorizado.
- [x] Diseño: grupos de menú únicos/desplegables; formulario atención primero y KPI secundarios; tablas de usuarios legibles; acciones secundarias agrupadas; inicio orientado a tareas y código de seis casillas accesible.
- [x] Verificar suite completa, Chrome/Edge, móvil, filtros/exportación y revisión independiente. Guardar evidencias y comprobar hashes original y Excel.

Ruling: ejecutar de manera continua en esta sesión según autorización actual; el documento previo ya presenta correspondencia y brechas y el usuario aprueba corregirlas. Una sola revisión independiente al terminar. Los perfiles usan códigos de función, nunca números de trabajador. No crear módulos de hojas ocultas por defecto. Conservar las vistas calculadas como aplazadas, sin simular resultados. Los conteos operativos permanecen disponibles.

Ruling: las fórmulas auxiliares no se copian como campos manuales. Unidad vale 1 por registro. G SOC abre Gestión social, no una tabla genérica de actividades. La fecha heredada no se clasifica automáticamente. Se corrigieron hallazgos de revisión sobre edición tras cambio de cargo y selección de vista; se corrigió una carrera de carga observada en el recorrido completo.
