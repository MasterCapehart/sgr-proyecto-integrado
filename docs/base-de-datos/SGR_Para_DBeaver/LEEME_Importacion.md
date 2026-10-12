# Importar el SGR en DBeaver

Este paquete crea **43 tablas y 94 claves foráneas** del dominio completo, no solo las de la segunda entrega. Incluye la distinción acordada entre delegación de origen y responsable. Atencion.id_delegacion conserva el significado de ORIGEN para compatibilidad; id_delegacion_responsable indica la encargada actual. Compromiso incorpora ambas referencias explícitas. El backend debe conservar origen y auditar cambios de responsable.

## Requisitos

DBeaver es el cliente: necesita conectarse a un servidor **MySQL 8.4** existente y en ejecución. No crea un servidor MySQL por sí mismo. El SQL no es para PostgreSQL ni SQLite. En este equipo no se pudo ejecutar el servidor instalado por una biblioteca faltante; no se volvió a iniciar Docker para esta entrega.

## Importación paso a paso

1. En DBeaver, seleccionar Nueva conexión > MySQL. Introducir host, puerto, usuario y contraseña del servidor que usarás. Probar conexión. Para un servidor local normalmente host es localhost y puerto 3306; usar los valores reales de tu instalación.
2. Conectar con una cuenta que pueda crear un esquema y tablas. No usar una base con información real para probar.
3. Abrir `01_Crear_Base_Completa_SGR.sql` en el editor SQL y asignarle esa conexión.
4. Ejecutar **el script completo**, no solo la sentencia seleccionada. Usar la opción de menú SQL Editor > Execute SQL Script; el atajo depende del sistema y la configuración.
5. El script crea `sgr_prueba`. No contiene DROP: si ese nombre ya existe, detenerse y elegir un nombre nuevo cambiándolo en ambos SQL. No ignorar errores para continuar.
6. Al terminar sin errores, actualizar el navegador de la conexión. Abrir la base > Tables. Deben aparecer 43 tablas. Ver campos en Properties/Columns y relaciones en Foreign Keys.
7. Seleccionar las tablas que deseas ver juntas y abrir el diagrama ER desde DBeaver. Para leerlo con claridad, mostrar grupos: acceso/organización, catálogos/atención, compromisos/evidencias y medición. El diseño draw.io también contiene páginas de detalle.
8. Ejecutar `02_Datos_Ficticios_Catalogos.sql` una sola vez, después de la estructura. Incluye una delegación, un cargo, rol/permiso, tipo/subtipo e ítem ilustrativos. Las otras tablas quedan vacías, listas para pruebas. No contiene cuentas ni contraseñas funcionales.
9. Ejecutar `03_Consultas_Verificacion.sql` y comprobar los conteos y la relación tipo/subtipo. Consultar datos mediante View Data.

## Lo que este paquete incluye y lo que requiere aplicación

Cobertura: usuarios, roles/permisos/ámbitos, recuperación, seis mantenedores, solicitantes y casos, actividades/atenciones, cargos/funciones/vigencias, evidencias y versiones, compromisos/estados/asignaciones/seguimientos/validación, conversaciones/mensajes, metas/indicadores/versiones/períodos/ajustes/resultados/alertas y auditoría.

La recuperación necesita generación/envío/verificación de códigos por Django; los campos no envían correos. Las tablas no sustituyen autorización, cifrado, auditoría inmutable, bloqueos por período, fórmulas aprobadas ni reglas de concurrencia. Consultar también el README del modelo anterior: las mismas reglas transaccionales siguen pendientes. Usuarios deberán integrarse con autenticación Django y las migraciones cuando se programe; el SQL no crea las tablas internas de un proyecto Django inexistente.

Los catálogos demo no son datos municipales. Longitudes, DECIMAL(18,6), nombres técnicos y versión MySQL son decisiones de diseño; confirmar contra valores reales antes de producción. Ninguna norma gráfica, SweetAlert2 o despliegue AWS se verifica importando tablas.

## Validación y limitaciones

Se comprobó estructura: PK, nombres/columnas, FK existentes y tipos compatibles. Se comparó con las 41 entidades del MER y las dos tablas técnicas documentadas (CargoFuncion y VersionEvidencia). Se mantuvieron XOR, unicidad de aportes, compatibilidad tipo/subtipo, integridad de contexto, revisión de versiones y límite de tres gestiones por caso. El cambio de origen/responsable se incorporó sin asignar una delegación fija a la persona.

**Ejecución en MySQL pendiente.** El paquete está listo para intentar la importación y examinarlo, pero no se declara perfecto ni probado en el motor. Si DBeaver muestra un error, conservar mensaje y sentencia; no quitar restricciones solo para conseguir importar. La demostración de persistencia y las pruebas de los requisitos necesitan ejecución real del sistema.
