# Transcripción de la reunión — contraste punto por punto

Revisión del 23/10/2026. Fuente: transcripción aportada por el usuario, conservada fuera del repositorio. La transcripción tiene errores de reconocimiento; los puntos ambiguos se identifican como interpretación, sin convertirlos en reglas nuevas.

Este contraste complementa la matriz R1–R13, no la sustituye. Los puntos de reunión TR01–TR22 se separan de los requerimientos posteriores. Metas territoriales, puntaje integral y puntos de felicitaciones se dejan para el final por instrucción del usuario.

| ID | Solicitud de la reunión | Estado observado | Evidencia y comprobación |
|---|---|---|---|
| TR01 | Resumen del trabajo y pendientes del funcionario | Integrado | `personal_progress.py`, `personal-progress.js`; suite `test_personal_progress`; colectivo de gestores es pantalla separada. |
| TR02 | Códigos automáticos en los registros y mantenedores | Integrado en flujos revisados | `auto_codes.py`, `code_reservation.py`, `capture_codes.py`; suites `test_auto_codes`, `test_code_reservation`, `test_capture_codes`. No se certifica cada pantalla por una sola prueba visual. |
| TR03 | Separar rol de acceso y cargo operativo | Integrado | `Usuario.rol` y `Usuario.cargo`, mantenedor de usuarios; `test_excel_workflow`, `test_area_catalog`. El cargo no concede permisos. |
| TR04 | Cargos y áreas basados en las funciones de la matriz | Integrado como catálogo y configuración | `area_catalog.py`, `matrix_profiles.py`, `docs/integracion/areas-excel/`; `test_area_catalog`, `test_area_items`. La asignación real a las cuentas debe mantenerse explícita; no se infiere una persona del Excel. |
| TR05 | Desactivar usuarios y evitar nuevos accesos | Integrado | `Usuario.is_active`, autenticación y autorización; suites `tests_acceso_permisos`, `test_local`, `test_revision`. |
| TR06 | Buscar vecino o registrarlo y reutilizar nombre, RUN y teléfono | Integrado | `neighbors.py`, `vecinos.js`, captura común; suites `test_neighbors`, `test_community`; aceptación transversal de vecino y captura. |
| TR07 | Delegación y datos del funcionario desde la sesión | Integrado | `active_delegation`, autor/cargo fijados en servidor; `test_capture_form.test_rechaza_autor_o_delegacion_inyectados`; no confiar en campos del navegador. |
| TR08 | Unificar el registro de actividad/atención | Integrado | `/api/captura/` y `registro-trabajo.html`; `test_capture_form` y `test_integral_workflow`. No implica que todos los conceptos sean una sola tabla. |
| TR09 | Mantener antecedentes y hasta tres gestiones sociales | Integrado | Extensión social de captura, `Atencion.caso_social`; `test_capture_form.test_cuarta_gestion_revierte_todo`, `test_excel_workflow`; sin compromiso huérfano ante error. |
| TR10 | Enviar opcionalmente la actividad/atención al tubo como agenda colectiva | Integrado | `capture_followup.py`, `captura-unificada.js`; `test_unified_capture`. Sin seguimiento no se crea compromiso. |
| TR11 | Un mismo código de origen y verificación del seguimiento | Integrado | `capture_followup.finish`, vínculo y código compartidos; `test_unified_capture` y aceptación transversal. El código no sustituye un archivo. |
| TR12 | Evidencia opcional y campo de archivo solo cuando corresponda | Integrado | `evidence`/`upload` en captura; se puede guardar sin archivo. La ausencia de evidencia impide aporte validado, no el registro de trazabilidad. |
| TR13 | En el listado de evidencias, abrir detalle y concentrar acciones dentro | Integrado | `operacion.js`: listado Ver detalle; descarga, aprobar, corrección, rechazar y anular en detalle según estado y permiso; suites `test_domain`, `test_closure`, `test_role_permissions_workflow`. |
| TR14 | No exigir enviar mensaje para aprobar/rechazar | Integrado bajo interpretación explícita | La revisión requiere observación de auditoría, no mensaje de conversación. La conversación permanece opcional. La frase transcrita no se interpreta como autorización para eliminar el módulo de conversación. |
| TR15 | Funcionario sin opciones administrativas | Integrado según permisos | Menú autorizado y API; `test_role_permissions_workflow`, `test_integral_workflow`, verificación UI seis perfiles. No se concede acceso por esconder/mostrar solamente enlaces. |
| TR16 | Mantener solicitud, acción, contacto, teléfono, territorio e ítem | Integrado | Captura y planilla; `test_capture_form`, `test_matrix`. Nombre/teléfono pueden faltar conservando trazabilidad, pero sin candidatura, según decisión posterior R5. |
| TR17 | Profesional involucrado para función de seguridad | Integrado | Campo condicionado a `GES_SEG`; opciones separadas de responsables asignables del tubo; `test_matrix.test_seguridad_asocia_profesional_configurado_sin_importar_personas`. |
| TR18 | Fecha de compromiso solo si ingresa al tubo | Integrado | `captura-unificada.js` controla visibilidad/obligatoriedad; pruebas de captura con y sin seguimiento. |
| TR19 | Funcionario responsable de sus propios compromisos; reasignación autorizada | Corregido en local en esta revisión | Existía restricción visual pero no validación equivalente en servidor. Ahora `capture_followup.can_assign` exige superusuario o `compromisos.editar_equipo`. Sin ese permiso: alta propia automática y prohibición de reasignar; afecta captura, atención, alta directa y edición. `test_followup_assignment` y verificación UI. |
| TR20 | Área de apoyo opcional y unidad automática | Integrado | Apoyo puede omitirse/vaciarse; unidad 1 del registro. `test_capture_form`, `test_matrix`, `test_followup_assignment`. |
| TR21 | Ítems que correspondan al cargo y meta asignada | Integrado como filtro de catálogo | `excel_support.items_for`, relación `ItemMeta.cargos`; `test_area_items`, `test_excel_workflow`. Incluye ítems generales y los del cargo; requiere configurar los vínculos reales y metas vigentes. |
| TR22 | Interfaz que no copie literalmente toda la planilla | Aplicado; validación de uso pendiente | Formulario común por secciones, selector de actividad por nombre, datos de sesión y extensiones opcionales; no es una aprobación de usabilidad de los participantes de la reunión. |

## Decisión de asignación aplicada

Se mantiene el permiso existente de gestión de equipo (`compromisos.editar_equipo`), sin crear nuevos roles ni dar permisos automáticamente. Esto conserva la facultad del coordinador cuando ya fue autorizado, además de administrador/delegado con ese permiso. El nombre del rol por sí solo no habilita el selector. Un funcionario sin ese permiso queda como responsable propio. La lista de profesionales de seguridad y los filtros del equipo no se reducen al aplicar esta restricción.

## Verificación del cambio TR19

- Pruebas iniciales reprodujeron asignación indebida en cuatro rutas y reasignación en edición.
- 7 pruebas específicas correctas tras la corrección: alta propia, rechazo y reversión atómica, edición sin cambios de versión ante rechazo, asignación autorizada, superusuario, listas separadas y avance de compromiso asignado.
- 56 pruebas relacionadas de captura, hitos, roles y aceptación integral correctas.
- Navegador local: captura y alta directa del tubo, responsable fijo de funcionario y selector de gestor autorizado; apoyo opcional y móvil sin desbordamiento.
- Regresión completa y evidencias: [resultado de esta revisión](RESULTADOS.md).

## Qué no se afirma

No se verificó la asignación real de todos los cargos, permisos y catálogos en AWS. No se eliminaron conversaciones ni se hizo obligatorio el cargo para toda cuenta basándose en una transcripción ambigua. No se actualizó el Excel ni se publicó esta corrección. La valoración institucional y los tres componentes pospuestos no se presentan como terminados.
