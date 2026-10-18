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
- [Documentación de entrega](docs/README.md): diagramas, evidencias y revisión de pendientes.
- [Plan de integración](docs/integracion/PLAN_TRASLADO_LOCAL.md).
- [Trabajo en equipo](CONTRIBUTING.md): ramas, commits por tarea y revisión antes de integrar a main.

## Despliegue y versión evaluada

- [SGR en AWS personal](https://54.236.112.203/pages/login.html), última verificación registrada el 18/10/2026.
- Versión de aplicación evaluada: `47358a26167f4efb0a4fe0638e78d815f821967a`; consultar [/api/version/](https://54.236.112.203/api/version/).
- [Instalación, configuración y recuperación AWS](docs/entrega/despliegue/README.md).
- [Resultados, incidencias y estado del paquete de evidencias](docs/entrega/README.md).

El acceso de evaluación debe acordarse con el docente por un canal privado. No hay credenciales compartidas en este README.

## Límites conocidos

La exportación de 10.000 atenciones bajo carga falló en el laboratorio (REN-EXP-01): falta corregirla y repetir el escenario. Los cálculos definitivos de metas y semáforos siguen fuera del incremento implementado; no se declaran aprobados.

Los períodos y la conciliación de metas tienen implementación y evidencias locales; consultar las limitaciones de cada informe. Las pruebas del laboratorio y las 49 comprobaciones del traslado personal tienen alcances diferentes y no sustituyen una aceptación integral de la versión final. Instalación desde clon limpio y rollback completo permanecen pendientes de ensayo.
