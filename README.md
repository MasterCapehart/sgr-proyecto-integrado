# Sistema de Gestión de Resultados (SGR)

Proyecto académico de un Sistema de Gestión de Resultados para delegaciones municipales, desarrollado con Django, MySQL e interfaz HTML/CSS/JavaScript. El backend sirve las pantallas y la API desde un mismo origen.

## Índice del proyecto

### Documentación y entrega

| Contenido | Qué encontrarás |
|---|---|
| [Documentación general](docs/README.md) | Índice de documentos y materiales de la entrega. |
| [Plan de tareas del equipo](docs/Plan_Tareas_Equipo_SGR%20%282%29.xlsx) | Organización y distribución de tareas. |
| [Diagramas UML](docs/uml/README.md) | Requerimientos, caso de uso general, casos específicos, clases y modelo de datos; imágenes y draw.io. |
| [Base de datos](docs/base-de-datos/README.md) | Diseño, diccionario y scripts de referencia. |
| [Mockups](docs/Mockups_SGR/README.md) | Catálogo de 20 pantallas, HTML navegables e imágenes de referencia. |
| [Pruebas locales y AWS](docs/pruebas/README.md) | Fichas Word, evidencias y el informe de cierre; separadas en [local](docs/pruebas/local/) y [AWS](docs/pruebas/aws/). |
| [Resultados y evidencias de entrega](docs/entrega/README.md) | Resultados, incidencias, cálculos revisados y estado documental. |
| [Instalación y recuperación en AWS](docs/entrega/despliegue/README.md) | Configuración, despliegue, respaldo y recuperación documentados. |
| [Aplicación en AWS](https://54.236.112.203/pages/login.html) | Acceso al sistema desplegado. |

### Código y colaboración

| Recurso | Qué encontrarás |
|---|---|
| [Backend](backend/) · [Guía de ejecución](backend/README.md) | Modelos, migraciones, API, configuración y pruebas. |
| [Frontend](frontend/) | Pantallas y componentes compartidos. |
| [Archivos de despliegue](deploy/aws/) | Configuración y procedimientos de despliegue. |
| [Plan de integración](docs/integracion/PLAN_TRASLADO_LOCAL.md) | Organización del traslado e integración de cambios. |
| [Trabajo en equipo](CONTRIBUTING.md) | Ramas, commits por tarea y revisión antes de integrar a main. |

## Ejecutar en local

Seguir [backend/README.md](backend/README.md). Cada integrante mantiene su propio `.env` y su base MySQL; Git comparte código y migraciones, no contraseñas ni datos locales.

## Módulos integrados

- **Acceso y recuperación de contraseña:** inicio de sesión y recuperación mediante código de verificación.
- **Usuario y contexto activo:** identificación del usuario, su rol y la delegación activa.
- **Mi progreso y pendientes:** resumen personal por mes, compromisos asignados, correcciones, revisiones autorizadas y actividad semanal.
- **Administración:** mantenedores de delegaciones, roles y usuarios.
- **Clasificación de actividades:** reglas versionadas por delegación, coordinación/ejecución/otra gestión y motivos de elegibilidad preliminar. No otorga puntos. [Funcionamiento y permisos](docs/integracion/BLOQUE_CLASIFICACION_ELEGIBILIDAD.md).
- **Ítems y metas:** administración de ítems y configuraciones de metas.
- **Tipos y subatenciones:** administración de ambos catálogos y sus asociaciones.
- **Captura unificada:** Mi planilla → Registrar actividad o atención; datos del vecino, junta de vecinos, ficha social y seguimiento opcional en el tubo, sin volver a capturar la solicitud.
- **Vecinos y organizaciones:** directorio por delegación, juntas y organizaciones comunitarias, pertenencias múltiples y rol de integrante o dirigente. [Funcionamiento, permisos y pruebas](docs/integracion/BLOQUE_VECINOS_ORGANIZACIONES.md).
- **Actividades y evidencias:** registro de trabajo por cargo, evidencia opcional y revisión de archivos por otra persona autorizada.
- **Hitos y festividades:** planificación interna con recursos descriptivos, responsables, avances y seguimiento opcional en el tubo. Ubicado en Planificación. [Funcionamiento y permisos](docs/integracion/BLOQUE_HITOS_FESTIVIDADES.md).
- **Compromisos y seguimiento:** gestión de compromisos, avances y conversación.
- **Alertas y auditoría:** consulta de alertas y registro de operaciones.
- **Planillas y exportación:** consulta de planillas y exportación a Excel.
- **Períodos de gestión:** administración de períodos, cierre y reapertura auditados.
- **Conciliación histórica:** vinculación y conciliación de metas históricas.

Los permisos deben asignarse explícitamente y los catálogos deben validarse con el equipo. Los indicadores incluidos son vistas del avance disponible, no una certificación del motor de cálculo definitivo.

## Despliegue y versión evaluada

- [SGR en AWS personal](https://54.236.112.203/pages/login.html), última verificación registrada el 23/10/2026.
- Versión de aplicación evaluada: `2e076870bb31a2779804b64f8340902c5ce0322b`; consultar [/api/version/](https://54.236.112.203/api/version/).
- [Instalación, configuración y recuperación AWS](docs/entrega/despliegue/README.md).
- [Resultados, incidencias y estado del paquete de evidencias](docs/entrega/README.md).

El acceso de evaluación debe acordarse con el docente por un canal privado. No hay credenciales compartidas en este README.
