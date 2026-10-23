# Actualización de diseño UML — 21/10/2026

## Estado y conservación

Análisis y diseño futuros; no constituye implementación, migración ni prueba de funcionalidades nuevas. Mantiene las carpetas y nombres previos, los once casos específicos y el resumen general. Amplía los lienzos para no borrar el contenido anterior. Reutiliza PersonaSolicitante como Vecino, sin introducir una segunda identidad desconectada.

En UML original se sincronizan los editables y las exportaciones principales PNG/JPG/PDF, los SVG de clases y sus fuentes JSON/PlantUML. El archivo de casos en doce pestañas conserva sus doce páginas. El lienzo conjunto conserva resumen superior y tres columnas de casos. La versión conceptual conserva su carpeta y sus clases previas, con ampliación identificada. Las versiones que describen esquemas físicos AWS/local y los informes Word de referencia no se alteran.

## Trazabilidad de los nuevos requerimientos

Los siguientes criterios son pruebas **previstas, no ejecutadas** de funciones futuras. Los controles efectuados en esta tarea se limitan a integridad y presentación de los artefactos.

| Fuente | Reglas / criterios de aceptación de diseño | Casos de uso | Clases / datos afectados |
|---|---|---|---|
| R1 | Mantener vecino; varias organizaciones con rol independiente; sin pertenencia activa duplicada; desactivación conserva historia | CU01, CU09 | PersonaSolicitante/Vecino, PertenenciaOrganizacion, Territorio, Delegacion |
| R2 | Mantener organizaciones y sus datos legales; socios desconocidos distintos de cero | CU09 | OrganizacionComunitaria, PertenenciaOrganizacion |
| R3 | Solo delegado/administrador crean; delegado asigna; funcionario solo actualiza sus tareas; recursos descriptivos; trabajo interno al tubo sin duplicación | CU02 | Hito, SerieHito, RecursoHito, AsignacionHito, Actividad, Compromiso |
| R4 | Beneficiario delegado → Otra gestión, aporte cero; no confundir autor ni destinatario de felicitación | CU01, CU04 | Actividad, ReglaElegibilidad, AporteIndicador |
| R5 | Sin nombre o teléfono conservar registro sin aporte | CU01, CU04 | PersonaSolicitante/Vecino, Actividad, ReglaElegibilidad |
| R6 | Máximo siete potencialmente puntuables por funcionario/fecha de realización; octava bloqueada, incluso con altas simultáneas | CU01 | CupoDiarioFuncionario, Actividad, ReglaElegibilidad |
| R7 actualizado | Tres días corridos inclusive; lunes/miércoles dentro, lunes/jueves fuera; tardío se guarda con aporte cero | CU01 | RegistroOperativo.creadoEn, Actividad.fecha, ReglaElegibilidad |
| R8 | Coordinación conserva seguimiento sin puntaje; ejecución final válida evaluable | CU01, CU02 | Actividad, ReglaElegibilidad, ValorCatalogo |
| R9 | Catálogo determina clasificación/elegibilidad; demás condiciones se comprueban en servidor | CU01, CU05 | ReglaElegibilidad, ValorCatalogo |
| R10 | Sobre120% registrar sin incrementar aporte ni cumplimiento; separar total realizado y computable | CU05, CU06, CU07 | ConfiguracionMeta, AporteIndicador, ResultadoIndicador, servicios de cálculo |
| R11 | Solo delegado registra/valida felicitación, con emisor, destinatario y respaldo formal verificables | CU03, CU04 | Felicitacion, PersonaSolicitante/Vecino, Usuario |
| R12 | Delegado registra ausencia; 20 días previstos−5 ausentes →75% de meta; sin doble descuento por solapamientos | CU05, CU06 | AusenciaFuncionario, ConfiguracionMeta, PeriodoMedicion, ResultadoIndicador |
| R13 | Mostrar individuo/equipo/territorio/delegación, distribución y bajos cumplimientos; respetar alcance por usuario | CU06, CU07 | ResultadoIndicador y servicios de consolidación; no tabla duplicada de tablero |

## Decisiones vigentes

- Funcionario registra/consulta/actualiza vecinos. Delegado/administrador mantienen organizaciones y pertenencias. Dirigente es rol de pertenencia, no atributo global del vecino. Pertenencia múltiple provisional.
- Recursos de hitos: descripción/cantidad, sin inventario ni presupuesto. SerieHito es propuesta de representación de recurrencia: no supone generación automática ya aprobada.
- Felicitaciones y ausencias: delegado. El administrador no obtiene ese permiso por analogía.
- Tres días son fechas calendario, no ventana móvil de72horas. Este acuerdo reemplaza el bloqueo semanal original de altas, no define aún ediciones/correcciones tardías.
- Siete actividades potencialmente puntuables consumen cupo por fecha de realización aun pendientes de validar. Actividades no puntuables no consumen cupo.
- Meta ajustada proporcional a días hábiles disponibles. Tope120% por funcionario/ítem/período sobre meta ajustada es alcance provisional, pendiente de pauta.
- Tableros: funcionario propio detalle; delegado equipo autorizado; administrador consolidado autorizado. Otros roles conservan permisos actuales; no se amplía su alcance nuevo sin acuerdo.

## Decisiones abiertas reflejadas como diseño provisional

Fórmula oficial, pesos, umbrales, redondeo, meta cero/ausencia total; interacción cupo/tope, anulación y liberación; modificaciones fuera de plazo; calendario y ausencias parciales; estados y recurrencia; quién desactiva vecinos; registros jurídicos y pertenencias entre delegaciones; asignación de puntaje/plazo/conflicto de interés de felicitaciones. Campos y tablas nuevas son propuesta lógica; no esquema físico definitivo.

## Controles de los archivos

Conservar IDs y posiciones principales previas, integridad de padres y terminales, XML legible, pares PNG/editable y sincronización de hashes. Regenerar exportaciones completas y revisar visualmente diagramas representativos, especialmente los grandes. Respaldo previo en99_Respaldos. No sustituye validación de las reglas pendientes con el responsable de evaluación.
