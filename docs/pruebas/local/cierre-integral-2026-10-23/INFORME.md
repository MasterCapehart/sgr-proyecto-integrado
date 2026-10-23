# Revisión integral del incremento — 23/10/2026

## Resultado

La comprobación local del incremento completa la brecha de pruebas entre módulos y distingue los seis perfiles. No equivale a aceptación institucional de todas las reglas ni a un despliegue nuevo.

- **552 pruebas Django**: resultado OK, con un fallo esperado preexistente. [Salida completa](regresion-django.txt).
- **4 escenarios nuevos de aceptación transversal**, con subcasos de permisos por rol: resultado OK. [Salida](aceptacion-transversal.txt), fuente `backend/core/test_integral_workflow.py`.
- **6 recorridos de navegador**: autenticación por API real y navegación con Administrador, Delegado, Funcionario, Coordinador, Verificador y Consulta. Vistas de escritorio y móvil sin errores JS ni desbordamiento horizontal. [Resultados](ui-seis-roles.json).
- **15 pares UML** conservados, 12 actualizados; geometrías y conexiones originales intactas. 133 conexiones de casos de uso sin atravesar cajas de otras actividades/actores/títulos. Se conservó margen exterior de imágenes y contención de compartimentos de clases. [Control UML](../../../uml/VERIFICACION_2026-10-23.json), [control de conexiones](../../../uml/VERIFICACION_LINEAS_CASOS_2026-10-23.json).

## Recorrido de datos ejecutado

Delegado publica regla de ejecución → crea organización → funcionario registra vecino → delegado registra pertenencia como dirigente → funcionario crea actividad con vecino, atención social y compromiso → se verifica que no hay duplicación ni compromiso huérfano → funcionario adjunta PDF → no puede autorrevisar → verificador distinto aprueba → funcionario consulta cumplimiento propio (1/10 = 10 %) → coordinador actualiza seguimiento del compromiso → delegado consulta aporte colectivo → delegado cierra período → cambios posteriores de meta no alteran el consolidado conservado → Consulta puede leer y no capturar.

Las pruebas adicionales distinguen Administrador **sin superusuario**, prueban permisos de lectura/escritura por seis roles y comprueban que dar permisos de equipo a otro perfil no evita la restricción expresa de gestión de ausencias/colectivo.

La inicialización de perfiles reutiliza permisos operativos de las pruebas existentes y las concesiones de las migraciones 0022–0024/0027. Esto no demuestra que cualquier rol nuevo creado manualmente reciba permisos automáticamente: la asignación explícita debe revisarse al administrar roles. No se ampliaron autorizaciones de producción.

## Matriz del navegador

| Rol de prueba | Pantalla revisada | Colectivo en menú |
|---|---|---|
| Administrador, sin superusuario | Indicadores colectivos | Sí |
| Delegado | Hitos | Sí |
| Funcionario | Registrar actividad o atención | No |
| Coordinador | Tubo de trabajo | No |
| Verificador | Bandeja de validación | No |
| Consulta | Mi planilla de trabajo, sin botón de alta | No |

La prueba de interfaz usa una base SQLite independiente y datos ficticios en `127.0.0.1:8014`; no son las cuentas ni los registros AWS. No se presenta este recorrido como repetición remota. Las reglas de plazos/cupos, ausencias, validación, anulación, tope y cierre concurrente se comprueban en sus suites de la regresión, además del escenario transversal.

## Correcciones y artefactos

- Añadida cobertura explícita de seis roles y del flujo transversal, sin cambiar reglas de negocio que ya pasaban.
- Corregido texto de Inicio: ya existe cumplimiento de actividades; el puntaje integral sigue pendiente. Cambio local en `frontend/index.html`, pendiente de publicar.
- Diagramas contrastados con código: tres fechas inclusivas, siete candidaturas, gestor administrador/delegado, candidatura frente a aporte validado, límite del 120 %, ausencias y colectivo. Se mantienen las carpetas y las conexiones.
- [Requerimientos, reglas, historias y aceptación](REQUERIMIENTOS_Y_TRAZABILIDAD.md).
- [Matriz R1–R13 en CSV](MATRIZ_TRAZABILIDAD.csv).
- [Definiciones pendientes para metas territoriales](METAS_TERRITORIALES.md).

## Límites y pendientes concretos

1. **Metas territoriales**: no se implementa un denominador inventado. Falta aprobar unidad territorial, responsabilidad, meta compartida, atribución y ajuste por ausencias. La distribución territorial actual sigue siendo conteo.
2. **Puntaje integral y felicitaciones**: el circuito formal existe; faltan reglas aprobadas para asignar su aporte a ítem/período y combinar componentes. No se confunde el índice de actividades con toda la evaluación.
3. **Prueba histórica esperada**: `core.tests_acceso_permisos.LoginLogoutTests.test_login_se_bloquea_tras_intentos_fallidos` utiliza las rutas antiguas `core.legacy_test_urls`. Conserva `@expectedFailure`. No se ocultó ni se presentó como fallo nuevo del login vigente: `local_api.access` tiene límite persistente por cuenta/IP y límite de sesión; la regresión conserva las verificaciones actuales.
4. **Diseño frente a esquema**: clases y ER siguen siendo modelos lógicos y conservan abstracciones históricas. No son una exportación física de todas las tablas. El informe Word y la copia externa `UML/` no se regeneraron; prevalecen los pares revisados en `docs/uml`.
5. La inspección visual UML fue representativa, más validación geométrica de todos los pares; no se afirma lectura exhaustiva de los 15 PNG a escala nativa.

No se modificó la base operativa ni el Excel, no se crearon datos de prueba en AWS y no se publicó este cierre documental.

## Contraste posterior de la transcripción

La reunión original se revisó punto por punto después de R1–R13: [matriz TR01–TR22 y corrección de responsable del tubo](../../../integracion/transcripcion-reunion/README.md). La asignación indebida se reprodujo y corrigió en local; las evidencias posteriores se mantienen separadas de la ejecución de 552 pruebas de este informe.
