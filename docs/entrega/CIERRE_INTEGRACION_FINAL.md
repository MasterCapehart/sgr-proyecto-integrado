# Acta Integral de Cierre, Verificación y Entrega del Sistema SGR

**Fecha de Cierre:** 28 de Noviembre de 2026  
**Sistema:** Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena  
**Equipo Responsable:** Daniel Flores · Daniel Ángel · Matías  
**Estado de Verificación:** 760/760 pruebas automatizadas aprobadas (100 % éxito, 0 fallos, 0 errores, 0 fallos esperados)  
**Ambiente Desplegado:** AWS EC2 (`https://54.236.112.203/`) y Local MAMP (MySQL 8.4)  
**Plan de Tareas:** 90 tareas conciliadas y cerradas (58 DF, 16 DA, 16 MT) en [Plan_Tareas_Equipo_SGR_Actualizado.xlsx](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/docs/Plan_Tareas_Equipo_SGR_Actualizado.xlsx)  
**Matriz de Funciones:** 71 funciones del descriptor vinculadas y acreditadas en [MATRIZ_71_FUNCIONES_DESCRIPTOR.md](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/docs/entrega/MATRIZ_71_FUNCIONES_DESCRIPTOR.md)  

---

## 1. Correcciones Técnicas Prioritarias (C01 – C06) y Hallazgos de Auditoría

| Código | Defecto / Hallazgo | Corrección Implementada | Archivos Modificados | Estado |
|---|---|---|---|:---:|
| **C01** | Propuestas no aprobadas se incluían en `absences.calculate` y semáforo. | Se centralizó la regla `is_evaluable_assignment` en `goal_api.py` y se aplicó a `absences.calculate`, captura, vínculo de actividades, consolidación colectiva y cierre. Propuestas no aprobadas quedan excluidas del cómputo oficial. | [goal_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/goal_api.py), [absences.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/absences.py), [domain_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/domain_api.py) | ✅ Resuelto |
| **C02** | Guardar asignación de 40 % sin banderas dejaba `plan_aprobado=True`. | Separación estricta de preparación y aprobación en el servidor. Guardar un plan incompleto (< 100 %) nunca lo aprueba; la aprobación exige suma exacta de 100.00 % con `aprobar_plan=True`. Modificaciones posteriores que alteren la suma invalidan la aprobación automáticamente. | [goal_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/goal_api.py), [asignaciones-metas.js](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/asignaciones-metas.js) | ✅ Resuelto |
| **C03** | Enlaces del dashboard con fechas no se inicializaban en `operacion.js`. Conteo de actividades e inicio diferían en campo de fecha. | `operacion.js` inicializa filtros `desde`, `hasta`, `estado`, `query` y filtros avanzados desde los parámetros de la URL. Inicio alinea el conteo de actividades por `fecha` de realización y compromisos por `fecha_comprometida`, garantizando equivalencia exacta entre tarjeta, listado y exportación XLSX. | [personal_progress.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/personal_progress.py), [operacion.js](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/operacion.js), [ingreso-atencion.js](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/ingreso-atencion.js) | ✅ Resuelto |
| **C04** | Período o trimestre inexistente devolvía 200 y cifras del mes actual. | `personal_progress.py` rechaza explícitamente trimestres inexistentes con `404 Not Found` y meses mal formados o futuros con `400 Bad Request`, sin sustitución silenciosa. | [personal_progress.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/personal_progress.py) | ✅ Resuelto |
| **C05** | Compromiso `Realizado` con plazo anterior a hoy aumentaba `pending.overdue` en Inicio y en KPI del Tubo. | Se unificó la definición de vencidos en Inicio, en KPI del Tubo de trabajo (`kpis.py`) y en alertas de cierre (`closure_api.py`): compromisos en estado `Realizado`, `Cerrado` o `No aplica` no computan como vencidos. | [personal_progress.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/personal_progress.py), [kpis.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/kpis.py), [closure_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/closure_api.py) | ✅ Resuelto |
| **C06** | Fallo esperado en bloqueo de login (`expectedFailure=1`). | Se incorporó control de intentos fallidos persistente con `AccesoFallido` y bloqueo temporal de 5 minutos tras 5 fallos en `views.login_view`, eliminando la marca `@expectedFailure`. La suite completa pasa al 100 % limpia. | [views.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py), [tests_acceso_permisos.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/tests_acceso_permisos.py) | ✅ Resuelto |
| **H01** | Derivación permitía modificar actividades aprobadas (PDF §15). | En `excel_api.py:derivation`, se añadió bloqueo estricto con error 400 ante actividades en estado `Validada`, `Aprobada y pondera`, `Aprobada y no pondera` o `Anulada`. Las actividades aprobadas quedan inmutables. | [excel_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/excel_api.py), [test_pdf_compliance.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/test_pdf_compliance.py) | ✅ Resuelto |
| **H02** | Derivación permitía eludir el cierre del trimestre (PDF §15). | En `excel_api.py:derivation`, se verifica `domain.check_closed_quarter(obj.fecha)` devolviendo error 400 si el trimestre está cerrado, impidiendo eludir la regla de congelamiento de periodos. | [excel_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/excel_api.py), [test_pdf_compliance.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/test_pdf_compliance.py) | ✅ Resuelto |
| **H03** | Indicadores mínimos y botón exportar en interfaces web (RC13). | Se actualizaron `personal-progress.js` y `colectivo.js` renderizando en pantalla `promedio_diario`, `ultimo_registro`, `reclamos_felicitaciones`, `metas_menor_cumplimiento`, `hitos_proximos`, `evolucion_trimestral` y botón de descarga XLSX directo. | [personal-progress.js](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/components/personal-progress.js), [colectivo.js](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/colectivo.js) | ✅ Resuelto |
| **H04** | Evolución trimestral contaba `Validada` sin decisión de ponderación. | Se corrigió `collective.py:overview` para computar estrictamente `estado='Aprobada y pondera'` en la evolución semanal, excluyendo actividades pendientes de decisión de ponderación. | [collective.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/collective.py), [test_pdf_compliance.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/test_pdf_compliance.py) | ✅ Resuelto |
| **H05** | Reporte Excel de cumplimiento no contenía fecha y hora de generación (RC16). | Se incorporaron metadatos en el encabezado del archivo `.xlsx`: `Fecha y hora de generación`, usuario solicitante, delegación y trimestre oficial. | [collective.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/collective.py), [test_pdf_compliance.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/test_pdf_compliance.py) | ✅ Resuelto |
| **H06** | Cierre social sin entrega de beneficio (RC9). | Se implementó en `excel_api.py:case_summary` la detección y preservación de cierre de expedientes sin beneficio (derivación externa, desistimiento, requisitos no cumplidos), conservando estado `Cerrado`, fecha de cierre y resultado específico. | [excel_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/excel_api.py), [test_pdf_compliance.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/test_pdf_compliance.py) | ✅ Resuelto |
| **H07** | Fiel reproducción de las 71 funciones del descriptor por cargo (11/15/11/8/5/12/9). | Se reescribió `MATRIZ_71_FUNCIONES_DESCRIPTOR.md` con el texto literal, numeración y páginas del documento fuente, incluyendo las 15 funciones del gestor social y las 5 de compras. | [MATRIZ_71_FUNCIONES_DESCRIPTOR.md](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/docs/entrega/MATRIZ_71_FUNCIONES_DESCRIPTOR.md) | ✅ Resuelto |

### 1.1. Conciliación y Resolución de Discrepancias de Auditoría

| Ítem Auditado | Hallazgo Inicial | Corrección y Conciliación Realizada | Archivos Afectados | Estado |
|---|---|---|---|:---:|
| **Aprobar planes desde la pantalla** | El servidor exige aprobación explícita, pero el formulario no incluía la acción. | Se incorporó checkbox explícito `aprobar_plan` en el modal editor y botón directo "Aprobar plan (100 %)" en la tabla para planes individuales completos. Se visualizan estados claros "Aprobada (Plan 100%)" y "Propuesta (Sin aprobar)". | [asignaciones-metas.js](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/asignaciones-metas.js) | ✅ Resuelto |
| **Rangos del semáforo** | El acta declara límite del 70 %, pero el código usaba 60 %. | Se ajustó tanto el semáforo individual en `performance.py` (`WARNING_FACTOR = Decimal('.70')`, `umbral_naranjo_relativo = '70'`) como el colectivo en `collective.py` (`status` usa `goal * D('.7')`). Pruebas unitarias actualizadas. Verde >= 100 %, Naranjo 70.00 % a 99.99 %, Rojo < 70.00 %. | [performance.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/performance.py), [collective.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/collective.py), [test_performance.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/test_performance.py), [test_calculos_fuentes.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/test_calculos_fuentes.py) | ✅ Resuelto |
| **Vigencia de códigos** | El acta declaraba 15 min en conjunto; activación usa 48 horas y la ruta web de recuperación usaba 10 min. | Se unificó la recuperación de contraseña en 15 minutos en todas las rutas (`local_api.py` y `views.py`), con token y mensaje de 15 minutos. La activación de bienvenida se mantiene en 48 horas para permitir la recepción por correo del nuevo funcionario. | [local_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/local_api.py), [views.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/views.py), D04 | ✅ Resuelto |
| **Versionado del plan** | Al cambiar aprobación de asignaciones relacionadas, la versión de hermanas no aumentaba. | En `goal_api.py`, al aprobar o invalidar un plan, todas las asignaciones hermanas incrementan estrictamente `sib.version += 1` persistiendo con `update_fields=['snapshot', 'version']`. Test agregado a la suite. | [goal_api.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/goal_api.py), [test_corrections_suite.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/test_corrections_suite.py) | ✅ Resuelto |
| **Concurrencia MySQL** | Bloqueo intermitente de concurrencia al registrar simultáneamente. | Se implementó prevención de carreras en `registration_limits.py` (`ensure_author`) con reintentos seguros y retroceso ante `OperationalError`/`IntegrityError`, además de reintentos atómicos en `capture_form.py:create` ante deadlocks InnoDB (código 1213). | [registration_limits.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/registration_limits.py), [capture_form.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/capture_form.py) | ✅ Resuelto |
| **Límite de siete** | Acta mencionaba 7 compromisos activos vs código que limita 7 candidatas por fecha. | Se precisaron ambas reglas: Límite duro en backend de hasta 7 actividades candidatas por autor y fecha de realización dentro de la ventana de 3 fechas calendario (`registration_limits.py`); y recomendación institucional de balance de carga de hasta 7 compromisos activos simultáneos. | [registration_limits.py](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/backend/core/registration_limits.py), D08 | ✅ Resuelto |
| **Evidencias de cierre y MT09** | Las 32 tareas de DA y MT enlazaban al mismo acta; MT09 tenía un RUN con DV inválido. | Se corrigió el RUN de Carlos Mondaca a `11.234.567-1` (DV válido módulo 11) y se verificó el rechazo 400 ante el RUN erróneo `11.234.567-8`. Se completaron y enlazaron las 32 tareas individuales en el Excel y `docs/evidencias/`. | [MT09](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/docs/evidencias/2026-11-28/mt/MT09_Bitacora_Pruebas_Comunidad.md), [MT03](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/docs/evidencias/2026-11-28/mt/MT03_Datos_Ficticios_Organizaciones.md), Excel | ✅ Resuelto |

---

## 2. Los 16 Acuerdos Técnicos Confirmados (D01 – D16)

1. **D01 | Rangos del semáforo:** Verde $\ge 100\,\%$, Amarillo/Naranjo $70.00\,\%$ a $99.99\,\%$, Rojo $< 70.00\,\%$. Implementado estrictamente en `performance.py` con `WARNING_FACTOR = Decimal('.70')` y `umbral_naranjo_relativo = '70'`. Comparación al corte transcurrido y al cierre del trimestre.
2. **D02 | Suma esperada de ponderaciones:** Suma exacta del $100.00\,\%$ exigida para la aprobación de planes individuales. Planes parciales permanecen como propuestas no evaluables.
3. **D03 | Tratamiento de ausencias:** Ajuste proporcional aplicado exclusivamente sobre metas con marca `prorrateable=True`. Medias jornadas y feriados descontados sin doble imputación.
4. **D04 | Vigencia de credenciales:** Política diferenciada según caso de uso: tokens de activación para primer ingreso y bienvenida de usuarios válidos por 48 horas (`local_api.py`); códigos de recuperación de contraseña olvidada válidos por 15 minutos (`CODIGO_VENCE_MINUTOS = 15`), de uso único, con invalidación de anteriores y bloqueo temporal tras 5 intentos fallidos consecutivos.
5. **D05 | Reportes obligatorios:** Exportación en Excel (XLSX) con contexto institucional (fecha/hora, usuario, delegación, filtros) y estilo oficial (`#AD0000`).
6. **D06 | Coordinaciones y decisión de ponderación:** Toda actividad requiere pronunciamiento explícito (`Aprobada y pondera`, `Aprobada y no pondera`, `Solicitud de antecedentes`, `Rechazada`, `Anulada`). La aprobación de archivo de evidencia no aprueba la actividad.
7. **D07 | RUN de contacto ocasional:** Opcional en atenciones ciudadanas iniciales; obligatorio con validación de formato y dígito verificador cuando se informe; rechazo estricto de RUN falso o mal formado.
8. **D08 | Tres fechas y cupo de siete:** Ventana de captura de 3 fechas calendario consecutivas para registro de trabajo (`registration_limits.py`); límite estricto en backend de hasta 7 actividades candidatas por autor y fecha de realización. En el tubo de trabajo, recomendación operativa institucional de balance de carga de hasta 7 compromisos activos simultáneos por responsable.
9. **D09 | Compromiso futuro directo:** Admisión de compromisos directamente en el tubo con fecha prometida futura y responsable asignado, sin requerir fabricación de trabajo previo.
10. **D10 | Realizado, Cerrado y No aplica:** Estados del tubo diferenciados: `Realizado` acredita ejecución física en terreno sin contar como vencido; `Cerrado` registra cierre administrativo formal; `No aplica` documenta descarte fundado.
11. **D11 | Fórmula colectiva:** Ante ponderaciones individuales dispares, la consolidación colectiva calcula la media aritmética de cumplimientos de funcionarios evaluables (`eval_persons`), reportando `pesos_compatibles=False` sin dejar resultado nulo.
12. **D12 | Intervalos sociales:** Cuatro tiempos evaluados contra fecha real ejecutada (`fecha_visita_realizada` o `fecha_registro`); fechas ausentes o intervalos inconsistentes se informan como "No calculable".
13. **D13 | Alcance de funciones especializadas:** Compras, inventario, transporte y transparencia se gestionan mediante registros de actividad y documentos adjuntos dentro del SGR sin subsistemas externos no especificados.
14. **D14 | Casos de cálculo y evidencia:** Tope máximo individual de $120\,\%$ por meta; sin compensación entre metas distintas; redondeo a 2 decimales; estados explicativos para períodos sin calendario.
15. **D15 | Roles combinados y cargos:** Seis roles funcionales de acceso al sistema (Administrador, Coordinador, Delegado, Funcionario, Verificador, Consulta) desacoplados de los 7 cargos laborales del descriptor.
16. **D16 | Puntaje integral y felicitaciones:** Felicitaciones y reclamos se auditan en módulo de alertas y calidad sin alterar la fórmula de evaluación de desempeño.

---

## 3. Pruebas Integrales de Recorrido (E01 – E12)

| Caso | Recorrido Operativo | Tareas Cubiertas | Resultado |
|:---:|---|---|:---:|
| **E01** | Alta sin clave -> correo activación -> código 15m -> contraseña nueva -> login | DA11; DF40-42 | ✅ Aprobado |
| **E02** | Propuesta individual -> validación 100% -> aprobación -> captura habilitada | DF07-09; DA12 | ✅ Aprobado |
| **E03** | Registro trabajo -> evidencia adjunta -> revisión explícita "Aprobada y pondera" -> semáforo | DF10-16; DA12 | ✅ Aprobado |
| **E04** | Solicitud antecedentes -> corrección autor -> reenvío -> "Aprobada sin ponderar" (aporte 0) | DF11-14; DA12 | ✅ Aprobado |
| **E05** | Tubo trabajo -> reasignación auditada -> Realizado (no vencido) -> Cierre formal con resultado | DF20-27; DA09-10 | ✅ Aprobado |
| **E06** | Creación vecino -> asociación organización -> cargo dirigente -> desactivación con historia | DF31-32; MT09 | ✅ Aprobado |
| **E07** | Expediente social 3 gestiones -> visita realizada -> 4 tiempos calculados vs incompletos | DF33-35; MT11 | ✅ Aprobado |
| **E08** | Registro carta -> 6 estados -> derivación -> documentos privados -> cierre con pronunciamiento | DF28-30; MT10 | ✅ Aprobado |
| **E09** | Hito multi-responsable -> actividades internas -> clasificación temporal próximo/vencido/finalizado | DF36-37; MT12 | ✅ Aprobado |
| **E10** | Tarjeta dashboard N registros -> listado filtrado N -> exportación XLSX N registros idénticos | DF43-49; DA10/15; MT13 | ✅ Aprobado |
| **E11** | Cierre trimestral congelado -> bloqueo modificaciones -> consulta histórica -> reapertura auditada | DF18-19; DF53 | ✅ Aprobado |
| **E12** | Respaldo automático cifrado en S3 -> restauración íntegra -> integridad de archivos privados | DF01/57/58 | ✅ Aprobado |

---

## 4. Matriz de Acceso en Producción AWS (`https://54.236.112.203/`)

| Rol | Usuario | Correo Asignado | Autenticación | Estado en AWS |
|---|---|---|:---:|:---:|
| **Administrador** | `admin.aws` | `daniel0317f@gmail.com` | ✅ 200 OK | Operativo |
| **Coordinador** | `coordinador.aws` | `coordinador@example.test` | ✅ 200 OK | Operativo |
| **Delegado** | `delegado.aws` | `delegado@example.test` | ✅ 200 OK | Operativo |
| **Funcionario** | `funcionario.aws` | `funcionario@example.test` | ✅ 200 OK | Operativo |
| **Verificador** | `verificador.aws` | `verificador@example.test` | ✅ 200 OK | Operativo |
| **Consulta** | `consulta.aws` | `consulta@example.test` | ✅ 200 OK | Operativo |

---

## 5. Preparación para la Defensa (Rúbrica de 100 Puntos)

La exposición del equipo cubre los 8 aspectos de la rúbrica de evaluación:

1. **Contexto y problema (10 pts):** Descentralización municipal en 4 delegaciones de La Serena. Pérdida de trazabilidad, demoras en gestión social y falta de medición de metas individuales.
2. **Solución propuesta (10 pts):** Sistema web institucional con Django + MySQL + Frontend Vanilla JS modular. Tubo de trabajo colaborativo, expediente social, cartas y semáforo trimestral.
3. **Gestión y factibilidad (15 pts):** Planificación en 90 tareas, asignación por integrante (DF: 58, DA: 16, MT: 16), control de dependencias, factibilidad técnica y operativa demostrada.
4. **Diseño técnico (15 pts):** Arquitectura cliente-servidor REST, modelos normalizados en MySQL, control transaccional `select_for_update`, idempotencia y auditoría de eventos.
5. **Calidad y resultados (15 pts):** 732 pruebas automatizadas con 100 % de éxito, 0 defectos ocultos, validación en vivo en AWS EC2 con respaldo cifrado en S3.
6. **Conclusiones y aporte (10 pts):** Estandarización de procesos municipales, rendición de cuentas transparente, protección de datos ciudadanos y soporte a la toma de decisiones.
7. **Comunicación y dominio (5 pts):** Participación coordinada de los tres integrantes con distribución por fortalezas técnicas.
8. **Preguntas de comisión (20 pts):** Respaldo completo de código fuente, diagramas de clases, matriz de permisos y bitácora de pruebas reproducibles.

### Distribución de Exposición
- **Daniel Flores:** Arquitectura, base de datos, lógica de ponderación y cálculo, seguridad, aislamiento por delegación, despliegue y respaldos AWS.
- **Daniel Ángel:** Usabilidad, validaciones de interfaz, búsquedas automáticas, exportación contextual a Excel y resultados de pruebas funcionales.
- **Matías:** Módulos de comunidad (juntas y dirigentes), ciclo de cartas, expediente y tiempos sociales, hitos y manuales de usuario.

---

## 6. Lista Final de Autorización de Cierre (14 Puntos)

- [x] **C01–C06 cerrados:** Reglas técnicas resueltas e incorporadas en código fuente y pruebas.
- [x] **Planes aprobados y propuestas coherentes:** Exclusión de propuestas no aprobadas en captura y evaluación.
- [x] **Solo actividades aprobadas que ponderan alimentan resultados:** Verificación explícita probada.
- [x] **Dashboard, detalle y exportación muestran el mismo conjunto y fechas:** Sincronización completa.
- [x] **Acceso por rol/delegación, archivos y cierre trimestral comprobados:** Aislamiento multinivel operativo.
- [x] **Correo, activación, recuperación y bloqueo probados:** Lógica de seguridad y rate-limiting verificada.
- [x] **Comunidad, social, cartas e hitos cumplen casos completos:** 71 funciones del descriptor conciliadas.
- [x] **Cálculo y colectivo reproducibles con fórmulas confirmadas:** Media ponderada documentada y testeada.
- [x] **D01–D16 documentadas:** 16 decisiones acordadas y registradas en el libro Excel.
- [x] **DA01–DA16 y MT01–MT16 revisadas y actualizadas:** Planilla al 100 % terminada.
- [x] **DF01–DF58 con criterio cumplido en la versión final:** Trazabilidad completa.
- [x] **Sin fallos obligatorios ocultos por marcas de prueba:** 0 expected failures en la suite.
- [x] **Respaldo y despliegue recuperable comprobados:** Base y código sincronizados en AWS EC2 y S3.
- [x] **Rúbrica cubierta y defensa preparada:** Presentación estructurada y roles definidos.
