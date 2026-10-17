# Operación SGR local — Implementation Plan

**Goal:** Conectar los módulos operativos a MySQL y trasladar el diseño de Mockups_SGR a las pantallas funcionales.
**Architecture:** Django conserva autenticación, autorización por delegación y auditoría. Un módulo de dominio agrega actividades, archivos privados, decisiones de revisión, compromisos e hilos; el frontend consume esas API sin datos simulados.
**Tech Stack:** Django 5.2, MySQL 8, HTML, CSS, JavaScript y SweetAlert2.
**Spec:** Requisitos_y_Plan_Pruebas_Segunda_Evaluacion_SGR.pdf y Guia_Proyecto_Software_SGR_Alumnos.pdf del directorio padre; Mockups_SGR/html y assets como referencia visual.

## Global Constraints
- Trabajar exclusivamente en sgr-eva2-local; sin GitHub, AWS ni correo externo.
- Excluir cálculos, ponderaciones y semáforos derivados. No mostrar métricas ficticias.
- Mantener los diagramas y los informes finales anteriores sin cambios.
- Mantener CSRF, permisos, delegación activa, auditoría y conflictos de edición.

## Review Focus
- Un usuario no puede leer ni descargar archivos de otra delegación.
- El autor no puede aprobar su propia evidencia.
- Una edición obsoleta debe producir conflicto y conservar el registro.
- Un archivo rechazado no debe guardarse ni quedar expuesto como recurso público.
- Los comentarios tienen contexto único, autor y fecha del servidor.

### Task 1: Persistencia y API de operación
Files: backend/core/domain_models.py, domain_api.py, domain_permissions.py, models.py, urls.py, migrations; test_domain.py.
- [x] Crear pruebas de creación, aislamiento, versiones, evidencia, revisión y conversación; ejecutar y observar fallo por rutas inexistentes.
- [x] Crear modelos con relaciones protegidas, código único, estados controlados e historial.
- [x] Implementar endpoints con permisos explícitos, filtros, paginación y archivos privados.
- [x] Ejecutar las pruebas nuevas y la regresión existente.

### Task 2: Diseño y pantallas conectadas
Files: frontend/assets/css/mockups.css, styles.css, components/layout.js, modules/operacion.js, pages y index.html.
- [x] Incorporar CSS y escudo de referencia manteniendo los identificadores funcionales.
- [x] Conectar actividades, evidencia, agenda, detalle, validación y reportes; retirar datos simulados.
- [x] Probar el ciclo actividad → evidencia → revisión y compromiso → seguimiento → conversación en navegador.

### Task 3: Verificación de entrega local
Files: scripts y .revision-local; docs/revision-local/Lista_Cumplimiento.md.
- [x] Revisar escritorio/móvil, errores de permisos, edición concurrente y descarga autorizada.
- [x] Ejecutar pruebas y guardar resultados reales, sin acreditar AWS ni envío externo.
- [x] Comprobar aislamiento del original y documentar límites pendientes.

## Execution
Ejecución directa autorizada por el usuario; no commits ni publicación. Registrar resultados aquí tras cada fase.

## Registro de ejecución

- Modelos y migración 0011 aplicados solo a sgr_eva2_local. No hay cambios de modelo pendientes.
- Pruebas iniciales de dominio: cinco fallos por rutas inexistentes; luego aprobación. Suite final: 154/154.
- Diseño: CSS y escudo de Mockups_SGR; controles conectados; ninguna copia del app.js simulado.
- Chrome y Edge: ciclo de actividad/evidencia/revisión, compromiso/seguimiento/conversación y XLSX aprobados.
- Seis mantenedores existentes y atención/auditoría: regresiones de navegador aprobadas.
- Configuración de metas: prueba visual detectó colisión de form.elements.item; corregida con namedItem; creación aprobada.
- Revisión independiente: dos hallazgos P2 corregidos con pruebas RED→GREEN (tipo de observación y reportes con permisos parciales).
- Aislamiento: hashes del original sin diferencias; copia sin remotos. Sin commits ni publicación.
- Limitación: no se acredita el 100% del plan documental completo; cobertura y exclusiones en docs/revision-local/Lista_Cumplimiento.md.
