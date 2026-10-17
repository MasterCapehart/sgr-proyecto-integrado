# Cierre local SGR — 15-10-2026

Se trabaja exclusivamente en `sgr-eva2-local`. No se publicó en GitHub ni AWS. El proyecto original conserva sus archivos.

## Cambios implementados

- Catálogos con historial por versión. Las atenciones y actividades nuevas capturan sus etiquetas; las capturas de registros antiguos se identifican como observadas y no reconstruyen un pasado desconocido.
- Protección de formularios con datos sin guardar al cancelar, navegar, cambiar contexto o salir. Los borradores no se almacenan en el navegador.
- Matriz de transiciones y permisos consultable, versionada y revisable en **Reglas y permisos**. La propuesta inicial no equivale a aprobación institucional; la validación local exige una acción explícita del responsable.
- Cierre de compromisos con atraso conservado. Reapertura separada con permiso y motivo; historial inmutable de cierres.
- Bandeja de alertas persistentes con motivo, responsable, vínculo, condición y revisión. Se detectan al consultar; no se afirma monitoreo en segundo plano ni envío de correo.
- Anulación autorizada de evidencias con motivo y auditoría. El archivo y sus revisiones se conservan; se actualiza el estado de la actividad.

## Verificación ejecutada

**184/184 pruebas de backend aprobadas** en MySQL temporal aislado. Registro por prueba: [variantes-automatizadas.csv](variantes-automatizadas.csv) y [JSON](ejecucion-unittest.json). Cada fila contiene precondiciones, comando, fuente, resultado, fecha y duración.

**12 comprobaciones de los nuevos flujos en Chrome y Edge**: [navegadores.json](navegadores.json). La regresión adicional está en [regresion-navegadores.json](regresion-navegadores.json). Una comprobación de acceso a pantalla no sustituye una prueba completa de cada operación.

Se realizó revisión independiente de código. Detectó riesgos de bloqueo en reglas globales y orden de bloqueos en evidencias/alertas; se unificaron los bloqueos. No se atribuye a esta inspección una prueba de carga concurrente.

## Trazabilidad y límites de aceptación

[Plan de 84 casos](plan-84-casos.csv): lista los identificadores reales y página del PDF; distingue las variantes vinculadas de la aceptación completa. **184 pruebas de código no significan 84 casos funcionales aprobados**. No se marca ninguno como aceptado por una persona que no lo revisó. Las variantes previas sin vínculo formal siguen disponibles en el registro y deben mapearse caso por caso antes de afirmar cobertura total.

Pendiente: revisión humana de permisos/transiciones y aceptación de los casos completos del PDF; AWS, publicación, correo externo y rendimiento del despliegue al final; cálculos de desempeño fuera del incremento autorizado.

## Reproducción

Desde esta copia:

```sh
backend/.venv/bin/python backend/manage.py test core --noinput --testrunner=core.closure_evidence.EvidenceRunner
node scripts/verificar_cierre_local.cjs
node scripts/revisar_entrega_local.cjs
python3 scripts/generar_evidencia_cierre.py
```

Las pruebas de navegador crean registros QA identificables en la base local; las pruebas de backend utilizan una base temporal. Las credenciales permanecen en archivos locales excluidos de Git. La versión comprobada se identifica en [version-archivos.json](version-archivos.json), sin atribuirle un commit inexistente.
