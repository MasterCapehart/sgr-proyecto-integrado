# Períodos y conciliación de metas — Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans task-by-task in the existing original checkout requested by the user. Preserve concurrent frontend work. Do not run stress tests yet.

**Goal:** Resolver duplicados históricos sin borrar filas y administrar períodos con fechas, cierre y reapertura auditada.
**Architecture:** PeriodoGestion como catálogo con estado activo y cierre independiente. ConfiguracionMeta conserva texto histórico y añade FK opcional para registros antiguos, obligatoria en nuevas altas API (el nombre/código antiguo se puede resolver a un período existente). Historial de versiones y eventos existente. Comando idempotente de conciliación con simulación previa.
**Tech Stack:** Django 5.2, MySQL local/RDS, JS nativo y SweetAlert2.
**Spec:** docs/requisitos/Requisitos_Segunda_Evaluacion.pdf B7 PAR-01, PAR-04, PAR-05; sin motor de cálculos PAR-02/03/06.

## Global Constraints
- No eliminar ni inventar fechas para metas históricas; no cambiar fórmulas ni ponderaciones.
- Conservar SVG oficiales, diseño existente, identidad Git del usuario y secretos privados.
- Operaciones versionadas, permisos por acción, cambios auditables y migraciones aditivas.
- No tocar docs/evidencias/2026-10-17/aws_redesign/ ni revertir commits INT-06/07.

## Review Focus
- Intervalos invertidos y bisiestos: duración inclusiva calculada por fechas.
- Cerrado no admite cambios de metas ni desvincularse para eludir cierre.
- Concurrencia al crear metas/cerrar período: mismo bloqueo del período antes del ítem.
- Duplicados con valores distintos: elegir solo única activa; si ambiguos, no conciliar automáticamente.
- Registros sin FK: conservar período textual; no asociarlos a fechas inventadas.

### Task 1: Pruebas y modelos
- [x] Escribir pruebas fallidas PAR-01/04/05, permisos, versiones, históricos y conciliación.
- [x] Agregar PeriodoGestion, FK y marca de conciliación; migración y restricciones SQL para fechas y meta nueva única por período.

### Task 2: API y conciliación
- [x] CRUD de períodos por patrón existente, opciones, cierre/reapertura con motivo y snapshots.
- [x] Conectar metas a períodos existentes y proteger períodos cerrados.
- [x] Comando conciliar_metas: simular, aplicar con actor/motivo, conservar filas y auditar.
- [x] Probar regresiones y consultar respaldo antes de aplicar conciliación local.

### Task 3: Interfaz e integración
- [x] Página Períodos con patrón actual, fechas, días, cierre y reapertura; navegación por permisos.
- [x] Selector de período en metas y etiquetas históricas; no romper estilos de INT-06/07.
- [x] Verificación navegador y suite completa; documentar alcance sin cálculos.

### Task 4: AWS
- [x] Respaldo previo privado, migraciones con identidad de despliegue, volver a usuario limitado.
- [x] Desplegar versión, comprobar flujo y datos; conciliar solo si existen grupos resolubles.
- [x] Commits separados por módulo y datos/evidencias, sin PR ni pruebas de estrés.

## Ledger
- Ruling: no se concilian automáticamente configuraciones que ya tienen calendario FK; etiquetas antiguas iguales no prueban identidad de fechas. La unicidad nueva utiliza ID de calendario, no etiquetas históricas.
- Los grupos locales QA se conciliaron con respaldo, sin borrar filas ni cambiar metas/ponderaciones.
- Una ejecución de suite se invalidó por solapamiento de procesos sobre la misma base temporal; repetir secuencialmente antes de declarar resultados. La base operativa no se utilizó como base de tests.

- Verificación final secuencial: 344 tests, 343 aprobados y 1 fallo esperado heredado. Recorrido local de navegador: 9 pasos aprobados.
- AWS pendiente: HTTPS no responde y EC2 devuelve UnauthorizedOperation. No se ejecutó migración remota; se pidió al usuario revisar Learner Lab.

- AWS completado tras iniciar Learner Lab: respaldo RDS privado, migración 0017 aplicada, ejecución con usuario limitado, servicio activo y recorrido real de navegador 9/9. Conciliación remota sin grupos. Evidencias: docs/evidencias/2026-10-17/periodos-aws/. El control EC2 por API sigue denegado; SSH y RDS operativos. No se ejecutaron pruebas de estrés.
