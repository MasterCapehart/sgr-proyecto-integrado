# Evidencia de revisión de registro y tubo — 23/10/2026

Entorno: pruebas Django sobre base temporal MySQL y navegador local con SQLite aislado en puerto 8014. No se crearon datos ni se modificaron permisos en AWS.

## Cambio confirmado

La pantalla limitaba el responsable del funcionario a su propia cuenta, pero el servidor aceptaba asignar a otra persona activa de la delegación. Se reprodujo en captura común, alta de actividad con seguimiento, atención con seguimiento, alta directa del compromiso y edición.

La comprobación se centralizó en el servidor para exigir gestión de equipo cuando cambie el responsable. La captura y la atención se revierten completas si la asignación no está autorizada. La fecha, apoyo opcional, unidad automática, código compartido y avance por el responsable permanecen disponibles.

## Resultados

- [Pruebas específicas de asignación](asignacion-pruebas.txt): 7 correctas.
- [Pruebas relacionadas](relacionadas-pruebas.txt): 56 correctas.
- [Regresión completa](regresion-django.txt): 559 pruebas, resultado OK con un fallo esperado preexistente.
- [Verificación de navegador](ui-asignacion.json): Funcionario y Administrador; captura y formulario directo del tubo, selección según capacidad de servidor y comprobación móvil.

El fallo esperado de la regresión pertenece a `core.tests_acceso_permisos.LoginLogoutTests.test_login_se_bloquea_tras_intentos_fallidos`, usando rutas antiguas. No se ocultó ni se convirtió en fallo nuevo del acceso vigente.

Fuente de aceptación nueva: `backend/core/test_followup_assignment.py`. Esta corrección y la matriz de la reunión se mantienen en local, pendientes de publicación.

Revisión independiente del cambio: no se identificaron regresiones concretas; se comprobó la separación entre responsables del tubo, profesionales de seguridad y filtros generales. Los hitos conservan su circuito de asignación autorizado propio.
