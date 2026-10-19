# Sistema de Gestión de Resultados (SGR)

Proyecto académico de un Sistema de Gestión de Resultados para delegaciones municipales, desarrollado con Django, MySQL e interfaz HTML/CSS/JavaScript. El backend sirve las pantallas y la API desde un mismo origen.

## Ejecutar en local

Seguir [backend/README.md](backend/README.md). Cada integrante mantiene su propio `.env` y su base MySQL; Git comparte código y migraciones, no contraseñas ni datos locales.

## Módulos integrados

Acceso y recuperación por código; usuario, rol y delegación activa; delegaciones, roles, usuarios, ítems, configuraciones de metas, tipos y subatenciones; registro de atención; actividades, evidencias y revisión; compromisos, seguimientos, conversación, alertas y auditoría; planillas y exportación Excel; períodos de gestión, cierre y reapertura auditados, y conciliación histórica de metas.

Los permisos deben asignarse explícitamente y los catálogos deben validarse con el equipo. Los indicadores incluidos son vistas del avance disponible, no una certificación del motor de cálculo definitivo.

## Organización y colaboración

- `backend/`: modelos, migraciones, API y pruebas.
- `frontend/`: pantallas y componentes compartidos.
- `deploy/aws/`: configuración y procedimientos de despliegue.
- [Documentación de entrega](docs/README.md): diagramas, evidencias y revisión de pendientes.
- [Plan de tareas del equipo](docs/Plan_Tareas_Equipo_SGR%20%282%29.xlsx).
- [Diagramas UML](docs/uml/README.md): requerimientos, casos de uso, clases y modelo de datos.
- [Pruebas locales y AWS](docs/pruebas/README.md): fichas, evidencias e informe de cierre.
- [Plan de integración](docs/integracion/PLAN_TRASLADO_LOCAL.md).
- [Trabajo en equipo](CONTRIBUTING.md): ramas, commits por tarea y revisión antes de integrar a main.

## Despliegue y versión evaluada

- [SGR en AWS personal](https://54.236.112.203/pages/login.html), última verificación registrada el 18/10/2026.
- Versión de aplicación evaluada: `47358a26167f4efb0a4fe0638e78d815f821967a`; consultar [/api/version/](https://54.236.112.203/api/version/).
- [Instalación, configuración y recuperación AWS](docs/entrega/despliegue/README.md).
- [Resultados, incidencias y estado del paquete de evidencias](docs/entrega/README.md).

El acceso de evaluación debe acordarse con el docente por un canal privado. No hay credenciales compartidas en este README.
