# Períodos y conciliación histórica — ejecución local

## Entregado en código
- Administración → Períodos de gestión: altas, consulta, edición, búsqueda, paginación, Excel y estado activo.
- Fechas reales con duración inclusiva: 90 o 91 días para el trimestre según el año; rechaza intervalos invertidos.
- Cierre/reapertura con permiso independiente, motivo y versión. El historial conserva capturas; las metas cerradas no se editan ni se desvinculan para eludir el cierre.
- Nuevas metas vinculadas a un calendario activo/abierto. Las etiquetas históricas sin fecha se conservan sin inventar calendarios.
- Unicidad SQL por ítem e ID de calendario. Etiquetas antiguas iguales no fusionan calendarios distintos.
- Conciliación idempotente: simula por defecto, aplica con administrador/motivo, conserva filas/valores y audita. No decide casos ambiguos ni fusiona calendarios ya vinculados.

## Conciliación realizada
Se conservan las configuraciones 2, 3, 5 y 6 y sus valores. Las repetidas 3 y 6 quedaron inactivas y vinculadas a 2 y 5, respectivamente. Criterios: única configuración activa y valores idénticos. Cero grupos históricos no conciliados después de aplicar. Respaldo SQL y exportación previa privados en `.integracion/periodos`, excluidos de Git.

## Verificación
- `python backend/manage.py test core --noinput`: 344 ejecutadas, 343 aprobadas, 1 fallo esperado del login antiguo bajo URL de pruebas heredada.
- Incluye pruebas reales con conexiones MySQL simultáneas: altas duplicadas, cierre frente a alta y cierre frente a edición.
- Navegador local: crear período bisiesto, vincular meta, cerrar, bloqueo de edición, reabrir, editar, consultar historial, exportar y vista móvil.
- `makemigrations --check --dry-run`: sin cambios pendientes de generar.
- Revisión estática independiente final: sin hallazgos bloqueantes; las pruebas de concurrencia se ejecutaron después de esa revisión.

## Pendiente remoto y alcance
El despliegue AWS de este módulo no está confirmado: la IP dejó de responder y la cuenta devolvió `UnauthorizedOperation` al consultar EC2. No se ejecutó la migración en RDS. Revisar Learner Lab/perfil `sgr-aws`, obtener respaldo remoto, aplicar migración 0017 con la identidad de despliegue y comprobar el flujo antes de declarar AWS aprobado.

No se implementó motor de cálculo, validación de suma de ponderaciones por cargo ni semáforos. Las capturas de cierre contienen parámetros, no resultados calculados. Pruebas de estrés, carga, restauración y el resto de la aceptación AWS se harán posteriormente según el documento.
