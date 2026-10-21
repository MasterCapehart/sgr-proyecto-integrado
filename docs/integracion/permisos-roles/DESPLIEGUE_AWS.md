# Despliegue en AWS Personal — Validación de Permisos y Roles

Fecha: 21 de octubre de 2026.
URL: https://54.236.112.203
Versión desplegada en vivo: `1bd20e079cdccc6fb53491972eb36d386910e209`

## Resumen del Despliegue

1. **Integridad y Respaldo**:
   * Se generó respaldo SQL completo previo de MySQL en RDS (`sgr-mysql-e5b5ae93a420`), cifrado con AES-256 en S3 (`sgr-evidencias-e5b5ae93a420`) con un peso de 2.773.241 bytes.
   * La aplicación se actualizó al commit `1bd20e079cdccc6fb53491972eb36d386910e209`.
   * Los servicios `sgr.service` (Gunicorn) y `nginx` se reiniciaron y reportaron estado `active`.
   * `/api/health/` responde `{"status": "ok"}` y `/api/version/` confirma la versión `1bd20e079cdccc6fb53491972eb36d386910e209`.

2. **Verificación de Permisos en Producción AWS**:
   * Se comprobaron 27 aserciones transaccionales mediante AWS SSM sobre la instancia EC2 (`i-075637109268f7efe`) y RDS:
     * **Funcionario**: Registro exitoso de actividad y seguimiento al tubo; bloqueo estricto en `/api/roles/`, `/api/usuarios/`, `/api/delegaciones/`, `/api/periodos/` y `/api/auditoria/` (403). Bloqueo de auto-revisión de evidencias.
     * **Verificador**: Consulta de evidencias ajenas, solicitud de corrección con observación obligatoria y aprobación final; bloqueo de acceso a administración y creación de actividades.
     * **Coordinador y Delegado**: Visibilidad de actividades y compromisos del equipo; edición y supervisión de compromisos ajenos con auditoría registrada.
     * **Consulta**: Visualización permitida; cualquier operación de escritura rechazada con 403 Forbidden.
   * Rollback atómico final completado sin residuos persistidos en la base operativa.
