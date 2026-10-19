# Mi progreso y pendientes personales

Versión desplegada en AWS personal: `2af785be26883ef336941651a5665d1e31a6bb3e`.

## Comportamiento

- El inicio muestra tareas personales antes del resumen operativo general.
- Los compromisos personales son los asignados al usuario. Se priorizan vencidos, correcciones, revisiones autorizadas y próximos plazos.
- Las actividades y atenciones se cuentan por autor, dentro del contexto autorizado de la delegación activa.
- Las evidencias personales corresponden a actividades propias y versiones vigentes, excluyendo anuladas y reemplazadas.
- «Esperando revisión» es trabajo enviado a otra persona. «Debes revisar» requiere permisos de consulta y revisión, y excluye evidencias y actividades propias.
- Los pendientes abarcan todo el historial abierto. El selector mensual modifica las métricas y gráficos, no oculta pendientes antiguos.
- El porcentaje de compromisos usa el estado actual de los asignados al usuario y creados en el mes. Si no hay registros, no se calcula porcentaje. No equivale al motor de metas.
- Los accesos llevan al registro correspondiente. El gráfico dispone de una tabla de datos accesible. Hay estados vacíos, reintento ante error y diseño móvil.

## Verificación realizada el 18 de octubre de 2026

- 12 pruebas nuevas del endpoint y 8 pruebas existentes de indicadores aprobadas en MySQL local de prueba.
- Regresión completa: 356 pruebas, 355 aprobadas y 1 fallo esperado heredado; sin fallos inesperados.
- Interfaz local comprobada en escritorio y móvil, con mes anterior y acceso al registro.
- [Comprobación de API en AWS](live-verification.json): 68 verificaciones aprobadas; acceso de perfiles, permisos de revisión, períodos, enlaces, cierre de sesión y versión. La cuenta de verificación estaba habilitada durante esta ejecución.
- [Comprobación de interfaz en AWS](ui-live.json): 7 verificaciones aprobadas con el perfil Funcionario, incluido móvil sin desbordamiento y ausencia de errores JavaScript.

Estas verificaciones no crean ni editan registros de negocio remotos. El inicio y cierre de sesión generan sus registros normales de sesión y auditoría. No sustituyen la carga ni la aceptación integral de otras funciones.

## Despliegue

Se comprobaron las huellas de los archivos remotos de partida. Se conservaron una copia de los archivos anteriores y de la configuración de versión en el servidor. El despliegue actualizó únicamente nueve archivos de aplicación y la identificación de versión, sin migraciones, cambios de datos, permisos, infraestructura ni del laboratorio. Se verificaron salud, versión, huellas y servicios activos después del reinicio de Django.
