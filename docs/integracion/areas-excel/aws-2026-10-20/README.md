# Despliegue de áreas e ítems en AWS — 20/10/2026

- URL: https://54.236.112.203/pages/cargos.html
- Commit de aplicación: `4a2555d025a248a82e350221f6537f88016eaac6`.
- Entorno: cuenta AWS personal. El laboratorio no se modificó.
- Se integró y publicó el código en `main` de GitHub, sin solicitud de revisión.

## Respaldo y aplicación

Antes de modificar archivos se verificó su versión previa y se preparó una copia recuperable de los archivos y la configuración. Se generó además un volcado de datos de 2.679.701 bytes, conservado en el servidor y respaldado con cifrado AES256 en el bucket privado. No se adjunta el volcado al repositorio, pues contiene datos del sistema. No hubo cambios de esquema ni eliminación de registros.

Las áreas y los ítems se cargaron dentro de una transacción: 12 áreas nuevas, 21 ítems nuevos y un ítem existente reutilizado, con 73 asociaciones. Se conservaron los códigos y la unidad histórica `1` del ítem reutilizado. Repetir la operación produjo cero altas y cero vínculos adicionales. No se cambiaron cargos asignados a usuarios ni roles.

## Incidencia resuelta

El primer intento se detuvo por una unidad de conteo histórica expresada como `1`; la transacción no guardó cambios parciales y el procedimiento restauró automáticamente los archivos y la versión anterior. Se añadió una prueba y compatibilidad para conservar ese conteo. El segundo intento concluyó correctamente. La restauración completa del volcado no fue necesaria ni se declara ensayada en este despliegue.

## Verificación

- 49 pruebas locales aprobadas de áreas, ítems, planillas y flujo Excel, incluyendo conservación de unidad histórica y rechazo de unidades incompatibles.
- `manage.py check` y comprobación de migraciones pendientes aprobados en AWS.
- Ocho archivos desplegados verificados por SHA-256; salud de la aplicación y versión confirmadas; servicios SGR y Nginx activos.
- Consultas autenticadas de la API verificaron las 12 áreas, los 22 ítems y las 73 asociaciones.
- Navegador: doce áreas visibles en una página; ausencia del botón de incorporación; columna Cargo / área operativa en Usuarios; ítem territorial compuesto vinculado a las cuatro áreas. Sin errores JavaScript durante este recorrido.
- No se presentan estas comprobaciones como una repetición integral de todas las pruebas del sistema.

Resultados: [verification.json](verification.json).
Capturas: [áreas](aws-areas.png) y [ítem territorial](aws-item-territorial.png).
