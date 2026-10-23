# Contraste UML con implementación — 23/10/2026

Se parte del estado modificado existente del 21/10. Respaldo local ignorado: `.integracion/cierre-integral/uml-antes-2026-10-23.zip`. Se conservan 15 pares, carpetas, IDs, geometrías y conexiones; 12 pares reciben etiquetas actualizadas. No se agregan conexiones entre módulos.

| Requisito | Evidencia de implementación | Representación y límites |
|---|---|---|
| R1–R2 | `../integracion/BLOQUE_VECINOS_ORGANIZACIONES.md`, migración 0022 | CU01/CU09, clases/ER lógicos. Vecino múltiple, vínculo único reactivable e historial. Funcionario edita vecinos; gestión y desactivación requieren permisos de administrador/delegado. |
| R3 | `../integracion/BLOQUE_HITOS_FESTIVIDADES.md`, migración 0023 | CU02. Gestores asignan; funcionario actualiza tareas propias. Recursos descriptivos y recurrencia manual vinculada; SerieHito permanece abstracción lógica. |
| R4–R5, R8–R9 | `../integracion/BLOQUE_CLASIFICACION_ELEGIBILIDAD.md`, migración 0024 | CU01/CU04/CU05. Catálogo versionado explícito, contacto y beneficiario; candidatura no equivale a puntos. Historial no reclasificado. |
| R6–R7 | `../integracion/BLOQUE_PLAZOS_CUPOS.md`, migración 0025; `backend/core/registration_limits.py` | CU01. Tres fechas inclusivas, siete candidatas por autor/fecha, reserva serializada, fecha fija y liberación al perder requisitos. Sin bloqueo semanal de alta. |
| R10 | `../integracion/BLOQUE_CUMPLIMIENTO_TOPE.md` | CU05/CU06/CU07. Candidatura + Validada + respaldos vigentes aprobados por otra persona y misma versión. Reconocido limitado a meta exacta × 1,20. Neutral sin evaluación; cierre conserva snapshot. |
| R11 | `../integracion/BLOQUE_FELICITACIONES.md`, migración 0026 | CU03/CU04. Ajuste posterior permite administrador/delegado con permisos; revisión separada del alta y nueva versión exige revisión. Sin puntaje ni cupo de actividades. |
| R12 | `../integracion/BLOQUE_AUSENCIAS_METAS.md`, migración 0027 | CU05/CU06. Calendario explícito, medias jornadas y solapamientos sin doble descuento. Gestores autorizados; funcionario propio. Snapshot privado al cierre. |
| R13 | `../integracion/BLOQUE_INDICADORES_COLECTIVOS.md`, `frontend/pages/colectivo.html` | CU06/CU07 y notas de cálculo. Administrador/delegado más ausencias.ver y ausencias.ver_equipo, delegación activa. Aporte reconocido/meta exacta por ítem; índice por pesos compatibles. Cobertura parcial, cierres conservados, territorio sin metas. |

Los documentos de bloque registran sus propias pruebas y despliegues; esta tarea no los repite ni acredita nuevas pruebas sobre AWS. Se consultan como evidencia junto al código. No se modifica producción.

Los seis perfiles históricos conservan su esquema de permisos; solo los roles canónicos Administrador, Delegado y Funcionario reciben las atribuciones documentadas para estos bloques. No se concede acceso por analogía a los otros perfiles. Un superusuario activo conserva el comportamiento explícito del servidor.

El modelo original incluye aportes/compromisos y servicios como abstracciones. El cálculo R10/R13 implementado reconoce actividades elegibles validadas, no cualquier compromiso cerrado. No hay motor integral que incluya felicitaciones, metas territoriales, inventario de recursos ni recurrencia automática. El documento del 21/10 es antecedente histórico de diseño; las decisiones resueltas y permisos posteriores se interpretan según este contraste.
