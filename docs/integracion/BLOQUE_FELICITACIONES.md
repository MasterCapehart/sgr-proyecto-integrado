# Felicitaciones y revisión formal — R11

Versión base desplegada y verificada en AWS el 22/10/2026. Versión de aplicación `b2a6addd1ae8f850789eb0a6d9b9c8ab340dcad4`.

## Alcance

Cambio posterior solicitado el 22/10/2026: administrador y delegado pueden registrar, editar, adjuntar respaldos y validar o rechazar felicitaciones. Un superusuario activo conserva su acceso completo. Los usuarios normales requieren rol activo y permisos de reclamos correspondientes; el ámbito de delegación se mantiene. Este ajuste está implementado y verificado en local, pendiente de despliegue. Los reclamos conservan su flujo y permisos anteriores. La consulta mantiene el alcance autorizado por delegación y por autor/equipo.

El administrador o delegado registra emisor, contacto cuando corresponda, fecha de recepción, descripción, procedencia, destinatario y opcionalmente funcionario reconocido. El alta queda pendiente; no equivale a aprobación. La clase del registro queda fija para impedir cambiar un reclamo a felicitación como vía alternativa.

Para validar se exige procedencia directa del vecino/usuario, destinatario delegado o delegación, emisor identificado, respaldo formal existente y observación explícita del administrador o delegado. Los mensajes personales no formalizados pueden conservarse, sin candidatura. La validación es una acción separada del guardado. El rechazo exige motivo y conserva trazabilidad.

## Respaldos e historial

Carga directa en el detalle: PDF, PNG o JPEG con firma compatible, hasta 10 MB. Se guardan nombre, tipo, tamaño, SHA-256, autor y fecha; claves de almacenamiento aleatorias, descarga por endpoint autorizado, sin enlaces públicos. El archivo formal es independiente de una evidencia asociada a otra actividad. El indicador anterior de medio escrito no sustituye el respaldo.

Se conservan respaldos y revisiones previos, incluyendo una instantánea de los datos revisados y la huella del respaldo. Cada edición o adjunto incrementa la versión del registro y exige una nueva revisión. Los conflictos devuelven 409; dos revisiones simultáneas de la misma versión no se sobrescriben.

Migración 0026: procedencia/destinatario en Reclamo, RespaldoFelicitacion y RevisionFelicitacion. Los registros anteriores conservan datos y quedan sin validación inferida. No se asignan nuevos permisos automáticamente.

## Interfaz y pruebas

Menú Gestión diaria → Reclamos y felicitaciones. El administrador y el delegado ven «Nueva felicitación»; los otros perfiles mantienen «Nuevo reclamo» según permisos. El detalle muestra primero el estado, respaldo y revisión; datos completos e historial son desplegables. Exportación incluye procedencia, destinatario, estado y candidatura formal, conservando protección contra fórmulas.

- 32 pruebas iniciales de felicitaciones y regresión del módulo de matriz correctas.
- Suite completa: 505 pruebas correctas, con un fallo esperado preexistente.
- 19 pruebas finales del bloque correctas, incluidas concurrencia y archivo desaparecido.
- Navegador local: alta pendiente, adjunto, validación, edición que invalida, rechazo con motivo, historial, interfaz móvil y administrador sin creación de felicitaciones.
- Revisión independiente: sin defectos bloqueantes confirmados.
- Modelos/migraciones sin diferencias pendientes, sintaxis JS y diff comprobados.

## Límites del incremento

Validada significa comprobación formal preliminar, no puntos otorgados. No se crean actividades, no se consumen cupos diarios ni se aplica el plazo de actividades a una felicitación independiente. Permanecen por definir la asignación de puntos/ítems/período, tratamiento de duplicados para cálculo y eventuales conflictos de interés. No se modificaron diagramas ni se implementaron los bloques siguientes.

## Despliegue AWS

Respaldo previo SQL cifrado en S3 y copia de archivos/configuración. Paquete, versión de partida y hashes comprobados; migración 0026 aplicada, sin ampliar permisos del usuario MySQL de aplicación. Servicios sgr y nginx activos; salud y versión comprobadas.

Comprobación autenticada de administrador, delegado y funcionario: solo delegado ve Nueva felicitación y pasa la restricción de rol de la API; otros perfiles reciben 403. Formulario de felicitación con guardado sin validar, procedencia/destinatario y controles de flechas uniformes. Historial anterior sin aprobaciones inferidas, interfaz móvil sin desbordamientos y sin errores JavaScript. No se crearon felicitaciones ni se cargaron archivos de prueba en AWS.

Las flechas de selectores simples se uniforman mediante selects.css desde el layout compartido; se ocultan en campos bloqueados, se mantiene teclado nativo y selección múltiple. Se actualizaron las referencias de caché de las páginas funcionales.

## Verificación del ajuste de administrador (local)

36 pruebas de felicitaciones y matriz correctas: administrador con permisos, superusuario sin rol y delegado pueden gestionar; otros perfiles siguen bloqueados. Alta pendiente y revisión separada se mantienen. Se actualizó el texto del formulario y la referencia de caché. Sin nueva migración.
