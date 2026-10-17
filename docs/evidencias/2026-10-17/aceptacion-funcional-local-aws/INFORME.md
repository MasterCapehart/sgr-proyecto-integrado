# Aceptación funcional local y AWS — SGR

Fecha de cierre: 2026-10-17T17:03:42-03:00. Código corregido: `6f4013a52bb4ba280ccadeb255cb7e683bd0cb9a`.
Rama: `feat/despliegue-aws`. No se abrió una solicitud de revisión ni se integró a main.
URL evaluada: https://50.17.79.145/pages/login.html
Fuente: `docs/requisitos/Requisitos_Segunda_Evaluacion.pdf`, especialmente A1–A3, B3–B6 y funciones operativas implementadas de agenda/evidencias/gestión social. Los apartados de cálculo no se declaran aprobados.

## Resultado ejecutivo

Se ejecutaron la suite Django local y recorridos reales contra MySQL local y AWS/RDS/S3. La suite final ejecutó **325 pruebas: 324 aprobadas y 1 fallo esperado heredado**. No hubo fallos inesperados.
Además se registran **316 comprobaciones AWS y 36 comprobaciones locales** de API y navegador, todas aprobadas en su ejecución final. Son comprobaciones de distinta granularidad, no un porcentaje de cobertura de todo el PDF ni una garantía de ausencia de defectos.

| Grupo | Comprobaciones finales | Resultado |
|---|---:|---|
| AWS API | 147 | PASS |
| AWS roles y gestión social | 111 | PASS |
| AWS metas corregidas | 10 | PASS |
| AWS navegador | 32 | PASS |
| AWS recuperación Gmail navegador | 7 | PASS |
| AWS operación navegador | 6 | PASS |
| AWS solicitud recuperación | 3 | PASS |
| Local navegador | 32 | PASS |
| Local metas corregidas | 4 | PASS |

Los fallos del ejecutor de pruebas se corrigieron antes de la ejecución final: la cuarta gestión social retorna 409, y la conversación debe localizarse en su contenedor con autor/fecha. Se comprobó visualmente que el mensaje ya estaba guardado. Estos dos ajustes fueron del ejecutor, no cambios del sistema.

## Funcionalidad comprobada

- Acceso mediante formulario real, campos vacíos con SweetAlert2, contexto permanente, cierre de sesión y API protegida.
- Seis mantenedores: crear, consultar, editar, cancelar, buscar, paginar, contar, exportar Excel, validar vacíos/duplicados/longitudes/formato y respetar relaciones. Desactivaciones permitidas y rechazos por referencias se comprobaron por API.
- Cargos y configuración de metas: operaciones API y restricciones. Las ponderaciones válidas por rango se verificaron; no se certifica suma institucional de pesos ni motor de cálculo.
- Seis perfiles de demostración: contexto, lectura y creación permitida/denegada según sus permisos; rechazo de cambio a delegación no autorizada y de acceso fuera del contexto.
- Atención: dependencias Tipo/Sub Atención, validación de combinaciones, asignación del responsable y delegación por servidor, persistencia, doble envío sin duplicar y guardado desde formulario.
- Gestión social: tres etapas, rechazo de cuarta gestión, consulta y exportación de expediente.
- Actividades: creación, edición, conflicto de versiones y estado validado tras revisión.
- Evidencias: carga real a S3, integridad de descarga, rechazo de acceso sin sesión/otra delegación, prohibición de autoaprobar y aprobación por otro verificador. También carga y revisión desde navegador.
- Compromisos: creación, conversación, cierre y reapertura autorizada por API; creación y conversación desde ficha en navegador.
- Reclamos: creación, edición y exportación. Alertas, auditoría, reglas, indicadores y planillas: consulta de los endpoints y carga de las pantallas.
- Recuperación: envío real desde AWS recibido por Gmail, código suministrado por el usuario, presentación de los seis dígitos, habilitación de nueva contraseña, rechazo de confirmación diferente, cambio persistido, rechazo de clave anterior, ingreso con nueva clave y verificación consumida. Se usó una cuenta ficticia; no se cambió la cuenta de administrador.
- Suite local: incluye pruebas de código erróneo/vencido/agotado, permisos, concurrencia, históricos, estados y validaciones adicionales. No se atribuye ejecución remota a estos casos por estar en la suite local.
- Chrome real automatizado y viewport móvil 390×844; sin errores JavaScript ni respuestas HTTP fallidas en el recorrido general de pantallas. No se afirma prueba física en todos los dispositivos/navegadores.

## Defecto encontrado y corregido

**Meta duplicada para un mismo ítem/período.** Se reprodujeron creación y edición incorrectas (201/200 en vez de rechazo). Se añadió validación en la API y bloqueo transaccional sobre el ítem para serializar las operaciones. Se agregaron tres regresiones: crear duplicado, editar para duplicar y permitir cambio propio/período diferente. La corrección pasó la suite y el caso real en AWS y local.

No se agregó una restricción SQL ni se modificaron datos históricos. Las escrituras administrativas externas a la API deben revisarse separadamente.

## Límites y asuntos que no se declaran terminados

1. En la base local siguen dos pares de configuraciones de prueba antiguas duplicadas: ítem 341, períodos `QA 92248949 207` y `QA Duplicado 92248949`. No se borraron ni reasignaron. La nueva API evita nuevos duplicados; estos datos históricos requieren conciliación explícita.
2. Creación/cierre/reapertura de períodos como entidad de calendario (PAR-01) no está implementada en esta versión; el campo período de una meta es texto. No confundir con cierre/reapertura de compromisos, que sí fue probado.
3. Motor de cálculo, fórmulas, ponderación total, semáforo calculado y resultados de desempeño siguen fuera del alcance acordado. Cargar una pantalla o un KPI operativo no valida esos cálculos.
4. El fallo esperado es `core.tests_acceso_permisos.LoginLogoutTests.test_login_se_bloquea_tras_intentos_fallidos` (nombre de clase real verificable en el archivo de pruebas), ejecutado con `core.legacy_test_urls`. Corresponde al login antiguo; la ruta pública usa `local_api.access` y tiene pruebas propias de límite persistente. No ocultar esta excepción como 325 aprobadas.
5. Los roles/catálogos y registros de AWS son de demostración. La aprobación municipal de permisos/datos oficiales y la revisión de identidad gráfica no se sustituyen por estos tests.
6. No se realizaron aquí carga/estrés, pentest, simulación de desastre, restauración de backup ni aceptación humana de todos los apartados B. No se declara 100 % del documento aprobado.
7. La disponibilidad AWS depende del Learner Lab. La corrección se desplegó y `/api/version/` identifica el código citado. El frontend local se sirve en http://127.0.0.1:8010/.

## Evidencias y reproducibilidad

La matriz CSV contiene cada comprobación API/navegador con el resultado real. Los JSON permiten revisar respuestas HTTP esperadas/obtenidas sin incluir cuerpos con datos o credenciales. El log Django conserva conteo y la excepción esperada. Las capturas muestran mantenedores, guardado de atención, móvil, recuperación y conversación.

Los scripts con cookies y datos privados de ejecución permanecen en `.integracion/aws-deploy/aceptacion`, excluido de Git. No se copian contraseñas, códigos, cookies, tokens, credenciales AWS ni configuración SMTP a esta carpeta.

Para repetir la suite: activar el entorno privado local y ejecutar `backend/venv/bin/python backend/manage.py test core --noinput`. Django crea y elimina su base de prueba temporal; no usar la base RDS operativa como base de tests. Los recorridos de AWS crearon datos ficticios marcados QA/UI/OPER; no se eliminó información previa.
