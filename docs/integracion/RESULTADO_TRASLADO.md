# Resultado del traslado — 17 de octubre de 2026

## Código y Git

El original se actualizó de 94d4c1c a 358a1ed antes de integrar el avance. Se creó feat/integracion-avance-local y se conservó la historia de los compañeros. El respaldo previo está fuera del repositorio. La copia aislada se conserva.

| Commit | Tarea |
|---|---|
| a7c8703 | INT-00 Plan, respaldo y exclusiones |
| 850407f | INT-01 Modelos y migraciones compatibles |
| a6b8ef8 | INT-02 API de acceso, catálogos y atención |
| 6fb8cb3 | INT-03 Operación, matriz e indicadores |
| b463802 | INT-02 Configuración parametrizada |
| 812618f | INT-04 Pantallas institucionales |
| 91ada6b | INT-05 Regresiones, panel técnico protegido e instalación |

Los commits siguientes incorporan estas evidencias y el estado de cierre. El frontend obtiene el token CSRF de la API, sin depender del nombre de cookie de la copia.

## Verificación realizada en la integración

- 316 pruebas ejecutadas sobre una base MySQL temporal, creada y eliminada por Django: sin fallos inesperados; una prueba heredada marcada como fallo esperado.
- El conjunto contiene 108 pruebas heredadas bajo URLs exclusivas de prueba y 208 del contrato integrado. Las heredadas no prueban la API de producción actual.
- Django check sin incidencias.
- Comparación de modelos con el estado de migraciones: sin cambios pendientes. Esta comparación se ejecutó sin consultar el historial de la base de la copia, porque su historial anterior no incluye la migración remota conservada. La suite MySQL construyó desde cero la cadena integrada completa.
- Archivo .env original verificado sin cambios mediante huella SHA-256. Revisión automatizada del contenido publicable y XML de documentos contra secretos de ambas configuraciones: sin coincidencias.
- Las evidencias de navegador adjuntas son históricas de la copia, no una nueva ejecución de navegador sobre la base original.

## Base y configuración original: pendiente

MySQL del original (127.0.0.1:8889) no respondió durante el diagnóstico de conexión. No se ejecutaron migraciones ni se copiaron registros sobre esa base. No se sustituyeron su configuración privada ni su contraseña por las de la copia.

Para poner en marcha el original falta iniciar su MySQL, respaldar la base existente y revisar `migrate --plan` antes de aplicar el esquema. El traslado de datos, usuarios, archivos adjuntos y configuración SMTP requiere comprobar esa base disponible y resolver posibles registros coincidentes. No se debe importar el volcado completo de la copia sobre datos del equipo sin conciliación.

Los archivos privados de la copia (buzón Gmail, cuentas de prueba, entorno MySQL, cachés, navegadores y scripts ligados a esa instalación) no se publican. Los archivos adjuntos ciudadanos y los datos de negocio no se incorporan a Git.

## Incidencias previas conservadas

- DEF-META-001: se reprodujeron configuraciones idénticas de meta para el mismo ítem/período; pendiente proteger esa regla.
- PAR-01/PAR-05: período con fechas y cierre/reapertura no implementado.
- AWS, cálculos definitivos y aceptación institucional pendientes.

Trasladar y publicar el avance no certifica cumplimiento del 100% de la entrega. Por indicación del usuario, se publica únicamente la rama; no se abre solicitud de revisión ni se integra a main. Los documentos bajo historico-desarrollo describen decisiones y resultados anteriores; no sustituyen este estado ni los README de instalación actuales.
