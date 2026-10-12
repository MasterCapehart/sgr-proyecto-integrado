# Base de datos SGR

El paquete `SGR_Para_DBeaver/` contiene el diseño completo y los scripts MySQL para crear una base local de prueba llamada `sgr_prueba`.

## Orden de uso

1. Conectar DBeaver a un servidor MySQL 8.4 en ejecución.
2. Leer `SGR_Para_DBeaver/LEEME_Importacion.md`.
3. Ejecutar el script completo `01_Crear_Base_Completa_SGR.sql` en una base de pruebas nueva.
4. Ejecutar una sola vez `02_Datos_Ficticios_Catalogos.sql` si se necesitan datos de ejemplo.
5. Ejecutar `03_Consultas_Verificacion.sql` y comprobar 43 tablas y 94 claves foráneas.

El SQL crea la base; no borra ni reemplaza una existente. Si `sgr_prueba` ya existe, detener la importación y revisar las instrucciones antes de continuar. No contiene datos personales reales ni credenciales de acceso.

## Trabajo en equipo

Cada integrante puede importar este paquete en su servidor local. Los datos locales no se comparten automáticamente y publicar cambios de SQL no modifica bases ya importadas.

Este paquete es una referencia previa a la implementación Django. Todavía deben crearse y versionarse los modelos y migraciones. Cuando se prepare Django, acordar una base vacía gestionada mediante migraciones para evitar intentar crear las tablas dos veces.

La estructura fue comprobada estáticamente; la ejecución en MySQL sigue pendiente según `Verificacion_Entrega.json`. Las reglas de autorización y transacciones necesitan backend. No se presenta este paquete como aplicación funcional ni como una prueba aprobada del motor.
