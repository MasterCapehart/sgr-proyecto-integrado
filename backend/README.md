# Backend

Tecnologías previstas en el diagnóstico: Django (Python) y MySQL.

Para conectar un frontend independiente, el backend deberá exponer una API. La biblioteca de API y las versiones quedan pendientes de acuerdo del equipo. No hay una aplicación ejecutable todavía.

Módulos previstos: usuarios y organización, actividades, agenda, evidencias y validación, indicadores y metas, reportes y auditoría.

El backend es responsable de autenticación, permisos, validación y persistencia. Las migraciones deben estar versionadas; las credenciales deben permanecer en la configuración local.

Documentar aquí la instalación, configuración, ejecución y pruebas una vez implementadas.



# Backend SGR (Sistema de Gestión de Resultados)

Este directorio contiene la API en Django para el proyecto SGR.

## Requisitos
- Python 3.10+
- MySQL Server

## Primeros pasos

1. **Clonar e ingresar al backend:**
   ```bash
   git clone [https://github.com/MasterCapehart/sgr-proyecto-integrado.git](https://github.com/MasterCapehart/sgr-proyecto-integrado.git)
   cd sgr-proyecto-integrado/backend
