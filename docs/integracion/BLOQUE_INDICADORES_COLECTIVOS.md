# Indicadores colectivos — R13

Estado: implementado, verificado en local y desplegado en AWS el 23/10/2026. Versión `2e076870bb31a2779804b64f8340902c5ce0322b`. Sin migraciones ni modificaciones al Excel o a los diagramas.

## Consulta

**Seguimiento → Indicadores colectivos**, página `frontend/pages/colectivo.html`. Administrador o delegado, además de permisos `ausencias.ver` y `ausencias.ver_equipo`. El funcionario mantiene su consulta individual. La API verifica el rol y los permisos aunque se escriba la URL directamente.

La delegación es siempre la activa autorizada en sesión. Filtros de período y equipo/área del cargo actual para períodos abiertos. Se incluye al personal activo relacionado con esa delegación, incluso por delegaciones autorizadas adicionales. No se combinan delegaciones.

## Cálculo

Se reutiliza R10/R12; no se duplican las reglas de candidatura, evidencia, validación o ajuste de ausencias.

1. Cada persona aporta únicamente unidades ya reconocidas con su tope individual de 120 %.
2. Para cada ítem: suma de unidades reconocidas / suma de metas ajustadas exactas de las personas evaluables × 100. No se redondean las metas antes de consolidar.
3. El índice de actividades normaliza los pesos de los ítems evaluables: suma(cumplimiento del ítem × peso) / suma(pesos). Requiere pesos compatibles por ítem y suma de pesos positiva. No mezcla cantidades de ítems con unidades diferentes ni promedia directamente porcentajes individuales.
4. El objetivo al día de cada ítem se pondera por las metas ajustadas de sus personas evaluables. El índice normaliza también los objetivos por pesos. Verde: alcanza objetivo; naranjo: al menos 60 % del objetivo; rojo: por debajo. Sin objetivo transcurrido: neutral.

Ejemplo: dos metas de 10; una persona realiza 13 actividades válidas, la otra ninguna. Se conservan 13 registros pero se reconocen 12; resultado colectivo 12/20 = 60 %. El excedente no compensa por encima del límite individual.

Sin calendario, disponibilidad o meta evaluable no se considera cero: se excluye del denominador y aparece en cobertura. El índice se identifica como parcial cuando falta evaluación de personas o ítems. Pesos incompatibles no producen un índice global; los porcentajes por ítem siguen disponibles. Un peso cero no genera una evaluación ponderada ficticia.

Este índice cubre actividades elegibles validadas. No constituye el puntaje integral ni incluye felicitaciones u otros componentes aún no incorporados al cálculo.

## Pantalla

- Índice colectivo, personas evaluadas, sin evaluación y personas en rojo/naranjo.
- Distribución gráfica del semáforo, con cifras y nombres accesibles.
- Metas conjuntas, aporte reconocido, exceso conservado, cumplimiento y cobertura por ítem.
- Resultado individual del equipo y enlace al resumen autorizado en períodos abiertos.
- Distribución operativa por territorio registrado en las actividades, normalizando espacios y mayúsculas. No existe una asignación de metas territoriales: no se inventa un porcentaje de cumplimiento territorial. Los registros sin territorio se identifican explícitamente.

Las áreas corresponden al cargo actual; no son un nuevo catálogo de equipos. El listado no publica nombres/contactos de vecinos, archivos ni motivos de ausencia.

## Períodos cerrados

Solo se consolidan snapshots de la delegación guardados al cierre; se conservan personas posteriormente desactivadas o trasladadas. No se reconstruye el equipo con usuarios actuales, ni se reemplazan metas cerradas con el catálogo vigente.

No se habilita filtro por áreas ni se reconstruye distribución territorial en cierres que no conservan estos atributos. Tampoco se enlaza desde filas históricas a un selector que solo conoce personas activas actuales. La pantalla indica que se trata del resultado conservado al cierre. Cierres anteriores sin cálculo R10 no reciben un cumplimiento inferido.

## Verificación

- 10 pruebas específicas: tope sin compensación, metas ajustadas distintas, cobertura, ausencia total, pesos incompatibles/cero, acceso por rol, anonimato, ámbito, datos sensibles, cierre y filtros inválidos.
- 548 pruebas de regresión correctas, con un fallo esperado preexistente.
- Navegador Edge local: respuesta real, vista de escritorio/móvil sin desbordamiento, menú autorizado, bloqueo de funcionario y ausencia de errores JavaScript.
- Revisión independiente: corregido enlace desde historial a persona no disponible en el selector actual.

Pruebas de datos en bases temporales y demostración SQLite local. Despliegue AWS con respaldo previo cifrado en S3, salud y versión verificadas. Comprobación real de administrador/delegado, bloqueo de funcionario y acceso anónimo, ámbito de delegación, límite de 120 % y vista móvil sin errores JavaScript ni desbordamiento. No se crearon registros de negocio de prueba en producción.
