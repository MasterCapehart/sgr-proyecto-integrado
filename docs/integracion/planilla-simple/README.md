# Planilla simplificada — AWS personal

Fecha: 21/10/2026. Versión de aplicación: `344697de9da6cb58772dd2560422daa156369498`.

URL: https://54.236.112.203/pages/desempeno.html?v=planilla-simple-1

- Tabla principal compacta: fecha, solicitud/trabajo, vecino/contacto, estado, siguiente paso y Ver detalle.
- Editar, adjuntar evidencia y derivar permanecen en el detalle con sus permisos.
- Filtros rápidos: todos, borradores, pendientes de revisión, correcciones y registros en el tubo; consultan la API y reinician la paginación.
- Reportes y columnas completas de exportación no se modifican. La exportación incluye los filtros vigentes.
- Solo cambia la presentación de Mi planilla de trabajo; las vistas de previsualización aisladas no se modifican.

## Verificación y respaldo

Navegador local y AWS: columnas compactas, petición de filtro al servidor, enlace de exportación con filtros, apertura del detalle con código original y acción de derivación disponible para usuario autorizado; móvil sin desbordamiento. No se guardaron registros de negocio durante estos ensayos.

Despliegue de tres archivos, con copia de archivos anteriores y respaldo SQL cifrado en S3 (2.780.391 bytes). Sin migraciones nuevas. Salud, versión, hashes y servicios SGR/nginx comprobados.
