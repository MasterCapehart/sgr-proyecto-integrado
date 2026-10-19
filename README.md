# Sistema de Gestión de Resultados (SGR)

Proyecto académico de un Sistema de Gestión de Resultados para delegaciones municipales, desarrollado con Django, MySQL e interfaz HTML/CSS/JavaScript. El backend sirve las pantallas y la API desde un mismo origen.

## Ejecutar en local

Seguir [backend/README.md](backend/README.md). Cada integrante mantiene su propio `.env` y su base MySQL; Git comparte código y migraciones, no contraseñas ni datos locales.

## Módulos integrados

- **Acceso y recuperación de contraseña:** inicio de sesión y recuperación mediante código de verificación.
- **Usuario y contexto activo:** identificación del usuario, su rol y la delegación activa.
- **Mi progreso y pendientes:** resumen personal por mes, compromisos asignados, correcciones, revisiones autorizadas y actividad semanal.
- **Administración:** mantenedores de delegaciones, roles y usuarios.
- **Ítems y metas:** administración de ítems y configuraciones de metas.
- **Tipos y subatenciones:** administración de ambos catálogos y sus asociaciones.
- **Atención ciudadana:** registro de atenciones con selección de tipo y subatención.
- **Actividades y evidencias:** registro de actividades, carga de archivos y revisión de evidencias.
- **Compromisos y seguimiento:** gestión de compromisos, avances y conversación.
- **Alertas y auditoría:** consulta de alertas y registro de operaciones.
- **Planillas y exportación:** consulta de planillas y exportación a Excel.
- **Períodos de gestión:** administración de períodos, cierre y reapertura auditados.
- **Conciliación histórica:** vinculación y conciliación de metas históricas.

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
- Versión de aplicación evaluada: `dd7f3d14145ff3b89b853b2e184b8461de78d4ac`; consultar [/api/version/](https://54.236.112.203/api/version/).
- [Instalación, configuración y recuperación AWS](docs/entrega/despliegue/README.md).
- [Resultados, incidencias y estado del paquete de evidencias](docs/entrega/README.md).

El acceso de evaluación debe acordarse con el docente por un canal privado. No hay credenciales compartidas en este README.
