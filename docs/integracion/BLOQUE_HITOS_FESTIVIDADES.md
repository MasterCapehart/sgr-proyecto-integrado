# Hitos y festividades — incremento local

Estado: desplegado y verificado en AWS el21/10/2026. Versión de aplicación `55156b2e4c4d8f41977ecb57f7ee4e2a3d37de15`.

Acceso: [Hitos y festividades en AWS](https://54.236.112.203/pages/hitos.html).

## Recorrido

1. En **Planificación → Hitos y festividades**, crear un hito con nombre, descripción, fechas, territorio y funcionarios responsables.
2. Agregar recursos descriptivos con cantidad y unidad. No se reservan existencias ni se calcula presupuesto.
3. En **Ver hito → Asignar actividad**, indicar tarea interna, responsable y plazo.
4. El funcionario asignado registra porcentaje de avance y observación. Cada actualización conserva autor y fecha en el historial.
5. Opcionalmente, el gestor selecciona **Enviar al tubo**. Se crea un único compromiso de origen **Interno**, vinculado a esa tarea. El compromiso muestra el enlace de regreso al hito.
6. El seguimiento del compromiso se realiza en el tubo, con las transiciones, observaciones y cierres existentes. No se generan atenciones ciudadanas ni vecinos ficticios.

## Permisos

| Perfil canónico existente | Alcance |
| --- | --- |
| Administrador / Delegado | Crear, consultar y editar hitos; asignar responsables y actividades; registrar avances y enviar tareas al tubo según el permiso de compromisos. |
| Funcionario | Consultar hitos asignados y sus propias actividades; registrar avance de esas actividades. El seguimiento en el tubo requiere sus permisos operativos habituales. |

Se limita cada operación a la delegación activa autorizada. La migración agrega permisos a los roles canónicos sin eliminar los anteriores; los roles personalizados no se amplían automáticamente.

## Decisiones de este incremento

- Estados de planificación: Planificado, En preparación, En ejecución, Finalizado y Cancelado.
- La finalización requiere actividades al100 % y compromisos vinculados realizados. Los hitos finalizados o cancelados conservan su historial sin edición ni reapertura en esta etapa.
- El porcentaje es avance informado de planificación, no puntaje ni cumplimiento de metas oficiales. No cierra automáticamente el compromiso.
- La recurrencia es informativa: se indica periodicidad y se crea cada realización manualmente. **Nueva realización** mantiene referencia a la anterior y copia los datos generales; fechas y tareas se planifican de nuevo. No hay programación automática.
- Se conservan miembros anteriores aunque una cuenta quede inactiva, para poder reasignar sus tareas sin perder el historial. Las nuevas asignaciones exigen cuentas activas de la delegación.
- Cada tarea tiene como máximo un compromiso. El origen interno no se puede convertir en externo. Los cambios autorizados de responsable y plazo en el tubo se reflejan en la tarea.
- Una tarea con plazo vencido debe actualizarse antes de crear su compromiso, para mantener las reglas de fechas del tubo. La planificación histórica permanece registrada.
- Migración aditiva `0023_hitos_festividades`; sin eliminación física.

## Validación

14 pruebas específicas aprobadas para permisos, aislamiento entre delegaciones, responsables, recursos, fechas, reintentos, versiones, avances propios, recurrencia, cierre, vínculo único al tubo y sincronización de responsable/plazo. Recorrido de navegador con cuentas ficticias locales y comprobación móvil aprobado. Suite core completa:461 pruebas, OK, con un fallo esperado previamente marcado en la suite. Sin cambios de modelos pendientes de migración.

No se modificaron los diagramas ni se implementaron los siguientes bloques de puntuación, ausencias e indicadores colectivos.

## Despliegue comprobado

Respaldo previo de archivos, configuración y base de datos; SQL cifrado en S3. Migración0023 aplicada correctamente; comprobación sin migraciones pendientes. Salud, versión y hashes de los archivos coinciden; servicios SGR y Nginx activos.

Pruebas autenticadas con administrador, delegado y funcionario: acceso al módulo, formularios según permiso y rechazo403 de creación para funcionario. Planificación aparece después de Gestión diaria (Reclamos y felicitaciones) y antes de Comunidad. Menú comprobado en escritorio y móvil: ocultar/mostrar, estado accesible y contenido sin columna vacía. No se crearon hitos de prueba en AWS.
