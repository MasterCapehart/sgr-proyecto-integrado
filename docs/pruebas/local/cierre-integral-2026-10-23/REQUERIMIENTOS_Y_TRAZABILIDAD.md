# Requerimientos y trazabilidad — cierre integral local 23/10/2026

## Alcance y evidencia

Esta matriz relaciona R1–R13 con código y pruebas existentes inspeccionados el 23/10/2026. **No certifica ejecución de pruebas en esta tarea ni producción.** Los resultados de ejecución del cierre deben leerse en la evidencia del responsable de verificación. «Implementado» describe presencia de reglas y cobertura en el repositorio; no constituye aprobación institucional de la pauta.

Fuente de numeración: `docs/uml/ACTUALIZACION_REQUERIMIENTOS_2026-10-21.md`. Fuente de acuerdos posteriores: documentos `docs/integracion/BLOQUE_*.md`, contrastados con módulos y pruebas. La versión procesable completa es [MATRIZ_TRAZABILIDAD.csv](MATRIZ_TRAZABILIDAD.csv). Módulos, modelos y migraciones se ubican en `backend/core/`; los nombres abreviados de métodos en una celda pertenecen al mismo archivo de pruebas salvo indicación contraria. Las migraciones se identifican por prefijo existente, sin proponer nuevas.

## Cambios de requerimiento y diseño histórico

- R7: el bloqueo semanal original fue reemplazado por tres fechas calendario inclusivas; el tardío se guarda sin candidatura. El cierre de período conserva sus propias reglas y no reinstala el bloqueo semanal.
- R3/R9: administrador y delegado gestionan hitos/catálogo con permisos. No se extiende la facultad a los demás perfiles por poseer otro permiso operativo.
- R11: el diseño del 21/10 decía «solo delegado». El ajuste posterior del 22/10 habilita también administrador con permisos, manteniendo revisión formal separada. Algunas secciones históricas de BLOQUE_FELICITACIONES describen la verificación previa y deben leerse con su ajuste final.
- R12: el diseño inicial reservaba ausencias al delegado; la regla posterior implementada habilita administrador y delegado con permisos y restringe al funcionario a consulta propia.
- R10: el límite vigente es 120 % por funcionario/ítem/período sobre meta exacta ajustada. Sustituye la nota histórica de 150 % del Excel; no se presenta como fórmula ya existente en ese libro.
- R13: la implementación habilita colectivo solo a administrador/delegado con `ausencias.ver` y `ausencias.ver_equipo`; no combina delegaciones. La parte territorial del requerimiento es distribución operativa, con metas territoriales pendientes.
- UML conceptual incluye nombres de diseño como SerieHito, AporteIndicador, ResultadoIndicador, ReglaElegibilidad o CupoDiarioFuncionario. No se deben interpretar como tablas físicas: la matriz usa los modelos realmente presentes y servicios de cálculo.

## Reglas, historias y aceptación

| ID | Historia | Regla y criterio de aceptación | UML | Estado y límite |
|---|---|---|---|---|
| R1 | Como funcionario mantengo vecinos y consulto sus organizaciones. | Permitir varias pertenencias con rol independiente; bloquear pareja duplicada; conservar historia y ámbito. | CU01;CU09 | Implementado. Territorio sigue siendo sector textual; confirmar alcance de pertenencias interdelegaciones. |
| R2 | Como administrador/delegado mantengo organizaciones comunitarias. | Socios desconocidos distintos de cero; desactivar con motivo sin borrar vínculos. | CU09 | Implementado. Validación institucional de campos legales y obligatoriedad pendiente. |
| R3 | Como gestor planifico hitos y asigno tareas; como asignado registro avances. | Administrador/delegado gestionan; funcionario solo tareas propias; un compromiso interno por tarea; avance no otorga puntos. | CU02 | Implementado. Recurrencia manual; recursos descriptivos. No inventario ni automatización. |
| R4 | Como capturador identifico explícitamente al beneficiario. | Delegado beneficiario implica Otra gestión sin candidatura; no confundir autor; normalizar RUN. | CU01;CU04 | Implementado. No inferir identidad por nombre. |
| R5 | Como funcionario conservo gestiones sin nombre o teléfono. | Guardar datos ausentes sin inventarlos; registro sin candidatura; corregir bajo regla/plazo capturados. | CU01;CU04 | Implementado. La elegibilidad no equivale a puntos efectivos. |
| R6 | Como funcionario conozco mis siete candidaturas por fecha de realización. | Octava candidatura rechazada atómicamente incluso concurrente; cupo compartido entre delegaciones; exclusiones no reservan. | CU01 | Implementado. La evidencia anulada no cancela actividad ni libera automáticamente cupo. |
| R7 | Como funcionario registro dentro de tres fechas calendario inclusivas. | Lunes a miércoles dentro; jueves conserva registro sin candidatura; America/Santiago; fecha de realización inmutable. | CU01 | Implementado. Reemplaza bloqueo semanal original. No interpretar como 72 horas ni excepción automática por reapertura. |
| R8 | Como funcionario distingo seguimiento de ejecución válida. | Coordinación y Otra gestión no aportan; ejecución solo candidata con regla explícita y requisitos cumplidos. | CU01;CU02 | Implementado. Los avances de hito no crean ejecución puntuable. |
| R9 | Como administrador/delegado publico reglas versionadas por delegación. | Sin regla no hay candidatura; publicación con motivo y versión; cambios no reescriben historia; servidor rechaza snapshot inyectado. | CU01;CU05 | Implementado. Requiere configurar catálogo real por delegación; no clasificar por palabras del nombre. |
| R10 | Como funcionario consulto cumplimiento sobre metas ajustadas. | Reconocer mínimo(válidas,meta exacta×1,20); validación y respaldos revisados por otra persona; conservar excedente; no evaluar sin base. | CU05;CU06;CU07 | Implementado parcial. Motor de actividades implementado; no certifica puntaje integral. Pauta oficial y otros componentes requieren validación de negocio. |
| R11 | Como administrador/delegado registro y reviso una felicitación formal. | Alta pendiente; procedencia vecinal directa, destinatario delegado/delegación, emisor identificado, respaldo real y observación; edición exige nueva revisión. | CU03;CU04 | Implementado parcial. Formalización implementada; puntos, ítem/período, duplicados de cálculo y conflictos de interés pendientes. |
| R12 | Como administrador/delegado confirmo calendario y ausencias; funcionario consulta lo propio. | Meta base×disponibilidad/previsto; medias jornadas sin doble descuento; cero/total neutral; cierre conserva snapshot privado. | CU05;CU06 | Implementado. Confirmar calendarios y selección de metas prorrateables reales; no importar fórmula Excel como regla idéntica. |
| R13 | Como administrador/delegado consulto equipo autorizado y distribución territorial. | Exigir rol y permisos de consulta/equipo; sumar reconocidos topados/metas exactas; cobertura explícita; territorio solo conteos; cierre no reconstruye equipo. | CU06;CU07 | Implementado parcial. No hay metas ni cumplimiento territorial. Véase METAS_TERRITORIALES.md; índice de actividades no es puntaje integral. |

## Casos de uso existentes reutilizados

Se verificaron los identificadores de los once diagramas específicos en `docs/uml/02_casos_de_uso/02_especificos/`: CU01 registrar actividades y servicios; CU02 gestionar agenda y compromisos; CU03 gestionar evidencias y códigos; CU04 validar actividades y evidencias; CU05 configurar funciones, metas y períodos; CU06 monitorear desempeño y alertas; CU07 generar informes y buscar información; CU08 colaborar y registrar observaciones; CU09 administrar organización, usuarios y catálogos; CU10 consultar trazabilidad y auditoría; CU11 acceder y recuperar contraseña. CU08/CU10/CU11 son soporte transversal (observaciones, auditoría, acceso); no se crean IDs nuevos para simular cobertura de las reglas pendientes.

## Cobertura y pendientes de validación de negocio

Las pruebas identificadas en el CSV son reales y cubren ejemplos concretos, pero su existencia no acredita que cada combinación de los seis roles haya sido ejecutada. Revisar además `test_role_permissions_workflow.py`, `tests_acceso_permisos.py`, `test_revision.py`, `test_integration_csrf.py`, `test_periodos.py` y `test_closure.py` para permisos, sesión, revisión y conservación histórica. Los cuatro perfiles distintos de administrador/delegado no heredan gestión de nuevos bloques por analogía; su acceso operativo depende del permiso y del ámbito del módulo.

Quedan por validar con el responsable de negocio: pauta integral de evaluación y pesos oficiales por ítem; contribución de felicitaciones (duplicidad, asignación y conflictos de interés); calidad del catálogo publicado; calendarios reales y metas seleccionadas para prorrateo; catálogo territorial, responsables y denominadores de metas compartidas. No se atribuyen fórmulas territoriales, puntos de felicitaciones ni componentes no implementados al índice colectivo actual. Véase [METAS_TERRITORIALES.md](METAS_TERRITORIALES.md).
