# Períodos de gestión: verificación en AWS

Fecha: 17 de octubre de 2026. Entorno: https://50.17.79.145.
Versión de código desplegada: 47358a2 (rama feat/despliegue-aws).

Se respaldó RDS antes de aplicar core.0017_periodos_y_conciliacion. El respaldo SQL privado permanece en el servidor; no se incluye en Git. Se conservó el usuario limitado de ejecución y se eliminó el archivo temporal de migración. Servicio sgr activo; comprobación Django sin problemas.

El recorrido real de navegador aprobó nueve comprobaciones: período bisiesto de 91 días, asociación de meta mediante selector, cierre con motivo, bloqueo en interfaz y servidor, reapertura, edición posterior, historial, exportación Excel y vista móvil sin errores JavaScript. Se utilizaron datos QA ficticios identificados en recorrido.json.

La simulación de conciliación en RDS no encontró grupos duplicados. No se copió la base local a AWS ni se inventaron fechas para registros históricos.

Alcance: comprobación funcional del módulo nuevo. No acredita pruebas de carga, estrés, restauración ni el cumplimiento completo de la entrega. El motor de cálculos continúa fuera de este cambio.

La API de control EC2 devolvió UnauthorizedOperation con el perfil actual; el despliegue se completó mediante SSH al servidor existente y conexión RDS. La gestión de infraestructura por CLI requiere revisar las credenciales/permisos del laboratorio.
