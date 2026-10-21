# Captura unificada — 21/10/2026

## Uso

Mi planilla de trabajo → **Registrar actividad o atención** (`pages/registro-trabajo.html`). La cuenta utiliza su cargo real y los ítems autorizados, sin selector de cargos ficticios. El acceso separado de Registrar atención se oculta para cuentas que pueden crear actividades; las rutas históricas siguen disponibles y no se eliminan registros anteriores.

El formulario guarda fecha, solicitud, acción, contacto, teléfono, sector e ítem. **Junta de vecinos** es texto opcional de hasta 200 caracteres. La unidad es uno por registro y no se escribe manualmente. Si no hay cargo, se muestra explícitamente esa situación y se permiten solo los ítems autorizados para la cuenta.

Con permiso de atenciones puede agregarse una ficha social; para cargo G_SOC aparece seleccionada inicialmente. Usa tipos/subatenciones activos, RUN validado y expediente nuevo/existente con hasta tres gestiones. Continuar una gestión conserva el solicitante del expediente y reutiliza su contacto. Los expedientes históricos permanecen en Gestión social. La nueva ficha enlaza a la actividad y sus evidencias; no genera una segunda actividad.

**Ingreso al tubo: Sí** agrega responsable, plazo, origen y área de apoyo. Reutiliza la solicitud, contacto, fecha y sector. El área de apoyo mantiene la obligatoriedad vigente del tubo. El formulario propone al usuario conectado y restringe el selector de responsable para funcionarios; las validaciones del servidor conservan usuarios activos y delegaciones autorizadas. No ingresar al tubo no significa resuelto.

La evidencia PDF/PNG/JPEG (hasta 10 MB) se ofrece solo con permisos de carga y edición; se guarda después de la captura y queda pendiente de revisión. Si falla el archivo, el formulario informa que el registro quedó guardado y permite abrir su detalle para adjuntar; no afirma que toda la captura haya fallado ni vuelve a crear la actividad. No existe aprobación automática.

## Persistencia y permisos

`POST /api/captura/`: actividad obligatoria, ficha social y compromiso opcionales. Una transacción abarca actividad/ficha/expediente/compromiso/auditoría. Una clave de idempotencia y huella completa impiden duplicados y rechazan reutilización con datos distintos. Los autores, cargo, plantilla, unidad y delegación son del servidor, no del formulario. Ítems y responsables se validan con las reglas vigentes.

`GET /api/captura/opciones/` requiere crear actividades y expone solo los catálogos mínimos de captura, incluidos tipos sociales únicamente si la cuenta puede registrar atenciones. No exige permisos de administración de catálogos. Consultar expedientes existentes requiere además el permiso de lectura de atenciones.

Migración 0019: columnas opcionales `Actividad.atencion` (relación uno a uno protegida) y `Actividad.junta_vecinos`. Se despliega también 0018 (idempotencia y seguimiento vinculado), pendiente en la versión anterior de AWS. No hay nuevas tablas ni cambio de roles, cargos asignados o datos históricos. Las columnas son aditivas y compatibles con restaurar los archivos anteriores.

## Validación

Pruebas nuevas de captura común/social, junta persistente, reintentos y cambios de payload, permisos sociales/de tubo, campos inyectados, error sin huérfanos, cuarta gestión y catálogos sin permiso administrativo. Regresión completa y navegador QA con datos ficticios, incluyendo PDF, navegación al detalle y vista móvil. Consultar el resultado adjunto.

El despliegue personal se registra tras comprobar respaldo cifrado, migraciones con credencial temporal, estado de servicios, versión y recorrido remoto. El laboratorio no se modifica.
