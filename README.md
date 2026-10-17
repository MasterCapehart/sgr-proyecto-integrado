# Sistema de Gestión de Resultados (SGR)

Aplicación municipal con Django, MySQL e interfaz HTML/CSS/JavaScript. El backend sirve las pantallas y la API desde un mismo origen.

## Ejecutar en local

Seguir [backend/README.md](backend/README.md). Cada integrante mantiene su propio `.env` y su base MySQL; Git comparte código y migraciones, no contraseñas ni datos locales.

## Módulos integrados

Acceso y recuperación por código; usuario, rol y delegación activa; delegaciones, roles, usuarios, ítems, configuraciones de metas, tipos y subatenciones; registro de atención; actividades, evidencias y revisión; compromisos, seguimientos, conversación, alertas y auditoría; planillas y exportación Excel.

Los permisos deben asignarse explícitamente y los catálogos deben validarse con el equipo. Los indicadores incluidos son vistas del avance disponible, no una certificación del motor de cálculo definitivo.

## Organización y colaboración

- `backend/`: modelos, migraciones, API y pruebas.
- `frontend/`: pantallas y componentes compartidos.
- `docs/`: requisitos, diagramas, acuerdos y evidencias.
- [Plan de integración](docs/integracion/PLAN_TRASLADO_LOCAL.md).
- [Trabajo en equipo](CONTRIBUTING.md): ramas, commits por tarea y revisión antes de integrar a main.

## Límites conocidos

Configuraciones de metas duplicadas (DEF-META-001) y períodos con cierre/reapertura (PAR-01/PAR-05) requieren trabajo adicional. AWS y cálculos definitivos quedan pendientes. Las evidencias históricas de la copia no sustituyen repetir la aceptación en cada entorno.
