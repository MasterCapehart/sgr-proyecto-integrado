# Cierre de brechas locales de la segunda evaluación

Alcance autorizado: copia sgr-eva2-local; historial CAT-04, cambios sin guardar A2, matriz de permisos B5, transiciones/alertas AGE-03/04, anulación EVI-05 y evidencias B20/B21. AWS, GitHub, correo externo, cálculos de desempeño y estrés del despliegue permanecen aplazados. No modificar original ni diagramas.

- [x] Pruebas RED de conservación histórica, anulación, cierre tardío, reglas de estado, alertas y permisos.
- [x] Migración aditiva: instantáneas de catálogos, versiones de catálogo, anulación auditable, cierres y alertas persistentes, política local versionada.
- [x] API y UI: estados permitidos desde política configurable, historial de atraso, alertas con enlace/revisión; evidencia anulada sin borrado; consultar versiones del catálogo y reglas/permisos.
- [x] Protección de borradores de todos los campos, navegación, contexto, recarga y cancelación.
- [x] Ejecutar suite, regresión y navegador; revisión independiente.
- [x] Preparar registro por variante, matriz de los 84 casos con estado honesto y versión local verificable; mantener pendientes de aprobación y nube explícitos.

Decisiones de integridad: registros nuevos capturan etiquetas y versiones al crearse. Las capturas de registros antiguos se identifican como observadas al iniciar el historial; no se atribuyen a su fecha original. La anulación conserva archivo y decisión histórica; no hay motor de puntuación. La política inicial se identifica como propuesta local, nunca como aprobación municipal. La aprobación funcional debe registrar una acción humana y versión concreta; no se falsifica ni se deduce de la ejecución de tests.

Resultados: 184 pruebas backend y 46 comprobaciones navegador (34 regresión + 12 cierre). Ver docs/revision-local/cierre-local/Informe_Cierre_Local.md. La aceptación completa de los 84 casos sigue pendiente; no se deduce de estas variantes.
