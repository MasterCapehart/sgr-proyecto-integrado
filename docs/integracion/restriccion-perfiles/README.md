# Gestión reservada a administrador y delegado

Fecha: 24/10/2026. Estado: implementado en local; pendiente de despliegue.

Corrige H01 y H02 de la auditoría de requerimientos del 23/10/2026.

- Solo los perfiles canónicos activos Administrador y Delegado pueden crear o editar hitos, asignar responsables, gestionar sus tareas y enviarlas al tubo. Cada acción sigue requiriendo su permiso correspondiente.
- Los mismos perfiles pueden publicar versiones del catálogo de actividades puntuables, con el permiso de configurar.
- El superusuario activo mantiene su acceso completo.
- Un permiso asignado accidentalmente a otro perfil no permite estas operaciones. El servidor rechaza la petición antes de modificar datos o devolver un reintento de escritura.
- Se mantienen la consulta autorizada y los avances de tareas asignadas a funcionarios. La reasignación desde el tubo también utiliza la comprobación estricta de gestor.
- La interfaz recibe capacidades comprobadas por el servidor para mostrar las acciones disponibles.

No modifica roles, cuentas, metas, reglas publicadas ni datos de AWS. No requiere migración.

## Verificación

Se reprodujo primero la creación indebida (201 en lugar de 403). La regresión específica cubre cinco perfiles ajenos al gestor con permisos asignados por error, creación/edición/asignación/envío al tubo, capacidades de consulta, publicación de reglas, gestores canónicos, permisos faltantes y rol inactivo. Las pruebas existentes verifican el acceso completo del superusuario y los avances del funcionario.

Las 30 pruebas de gestión reservada, hitos y elegibilidad pasan en local.

Revisión general: 591 pruebas ejecutadas; 590 pasan y se mantiene un fallo esperado preexistente de acceso en las rutas heredadas de pruebas. No aparecieron nuevos fallos. También se verificaron la sintaxis del módulo de hitos y los cambios de formato.
