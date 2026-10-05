# Sistema de Gestión de Resultados (SGR)

Proyecto Integrado: Sistema de Gestión de Resultados para Delegaciones Municipales.

## Organización

- `frontend/`: interfaz de usuario. Framework pendiente de acuerdo del equipo.
- `backend/`: backend previsto con Django y MySQL; expondrá una API para el frontend.
- `docs/`: requerimientos, UML, modelo de datos y acuerdos del equipo.
- `.github/`: plantillas para tareas y solicitudes de integración.

Este repositorio contiene la estructura inicial. Todavía no incluye una aplicación ejecutable.

## Primeros pasos

1. Clonar este repositorio.
2. Leer `CONTRIBUTING.md`.
3. Acordar el framework del frontend y las versiones de las tecnologías.
4. Configurar el backend, la base de datos y las instrucciones de instalación.
5. Implementar acceso y roles, seguido del registro de actividades y evidencias.

Cada parte deberá documentar sus comandos de instalación, ejecución y pruebas en su propio README cuando se implemente.

## Colaboración

Crear una rama por tarea, abrir un pull request y solicitar la revisión de otro integrante antes de integrar a `main`. Registrar tareas y responsables en GitHub Issues.

## Datos y configuración

No subir credenciales ni datos personales reales. Las configuraciones locales se guardan en archivos `.env` excluidos del repositorio. Los ejemplos deben usar valores ficticios. Las migraciones de Django se versionan junto al código.
