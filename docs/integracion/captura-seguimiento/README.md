# Captura y seguimiento vinculados — local, 20/10/2026

## Funcionamiento

Registrar atención y Nueva actividad incorporan **¿Requiere seguimiento en el tubo?**:

- **No requiere seguimiento:** guarda solamente la atención o actividad.
- **Sí, crear compromiso:** muestra responsable, plazo, descripción, área de apoyo y origen. La atención también pide sector, porque no existe como campo base. En la actividad se reutiliza el sector ya informado.
- **Vincular compromiso existente:** conserva la opción anterior, con los registros disponibles según rol y delegación.

La descripción del compromiso se rellena a partir del problema o solicitud y se puede ajustar. Solicitante/contacto, fecha de solicitud, usuario y delegación se toman del origen. El responsable se propone como el usuario conectado cuando está disponible; puede elegirse otro trabajador activo autorizado en la delegación. Área de apoyo se propone desde el cargo cuando existe y conserva las validaciones actuales. No se asignan roles o delegaciones nuevas ni se importan trabajadores del Excel.

Una atención puede crear directamente el compromiso: **no exige una actividad intermedia**. Gestión social conserva su expediente y hasta tres gestiones; elegir seguimiento no crea otra etapa.

## Persistencia y trazabilidad

Origen y compromiso se guardan dentro de una misma transacción. Si falla un campo, permiso, relación o la validación final del origen, se revierten ambos. Seleccionar un compromiso existente y crear otro a la vez se rechaza. El nuevo compromiso conserva la delegación activa y no permite asignar una delegación/autor/estado arbitrario desde los datos anidados.

Las nuevas actividades enviadas desde la interfaz incluyen una clave de idempotencia; las atenciones mantienen la suya. Una huella de la captura impide reutilizar una clave con datos diferentes. Los reintentos simultáneos devuelven el registro ya creado, sin duplicar el compromiso. Los clientes antiguos sin clave en actividades siguen siendo compatibles; para proteger sus reintentos deben enviar `clave_idempotencia`.

La referencia de foto del nuevo compromiso toma el código del origen. Esto no adjunta ni aprueba evidencia: los respaldos se cargan y revisan mediante su módulo. No se reescriben referencias de compromisos existentes.

Las altas de origen y compromiso quedan auditadas. El registro del compromiso incluye el tipo e identificador del origen. La interfaz permite:

- Abrir el compromiso vinculado desde una actividad, la atención detallada o la gestión social.
- Consultar los registros de origen desde el detalle completo o la ventana de un compromiso.
- Abrir una atención concreta en la nueva página `atencion-detalle.html?id=…`.

La consulta de orígenes filtra primero el compromiso por delegación/permisos y después cada tipo de origen por su permiso de lectura. Las actividades respetan además el alcance propio/equipo existente. Se muestran hasta 100 orígenes de cada tipo.

## API

Al crear una atención (`POST /api/atenciones/`) o actividad (`POST /api/operacion/actividades/`) se puede enviar:

```json
{
  "clave_idempotencia": "identificador-unico-de-la-captura",
  "compromiso": null,
  "nuevo_compromiso": {
    "responsable": 123,
    "fecha_comprometida": "2026-10-25",
    "descripcion": "Coordinar una respuesta al requerimiento",
    "sector": "Sector de demostración",
    "area_apoyo": "Área de demostración",
    "origen": "Externo"
  }
}
```

El ejemplo ilustra los campos adicionales; también deben enviarse los campos obligatorios del origen. Los datos son ficticios y el responsable debe existir y estar autorizado. Crear el compromiso requiere `compromisos.crear` además del permiso de alta del origen. Los controles de fechas y responsable reutilizan las reglas existentes del tubo. La creación conjunta se ofrece al registrar, no al editar un origen ya guardado.

`GET /api/seguimiento/opciones/` proporciona responsables autorizados para esta captura. `GET /api/operacion/compromisos/ID/origenes/` devuelve solo orígenes consultables. No se modificó el motor de metas ni el flujo de aprobación de evidencias.

## Base de datos y despliegue

Migración **0018_captura_seguimiento**: agrega tres columnas opcionales a tablas existentes: clave de idempotencia/huella en Actividad y huella en Atencion. No crea tablas adicionales ni modifica claves, asignaciones, códigos o vínculos anteriores. Fue aplicada en la base local MAMP y en la base independiente de demostración.

Este informe registra la validación local del 20/10/2026. La publicación posterior se documenta en [Captura unificada](../captura-unificada/README.md). Para desplegarla se requiere respaldo, publicar los archivos de aplicación, ejecutar la migración con permisos de esquema y verificar el recorrido remoto; copiar solo los HTML no es suficiente.

## Verificación local

- **401 casos** de regresión: **400 aprobados y un fallo esperado preexistente**, sin fallos inesperados.
- Trece casos específicos de captura unificada: creación desde ambos orígenes, ausencia de seguimiento, errores sin huérfanos, responsable ajeno, permisos, exclusión de vínculos simultáneos, lectura de orígenes y aislamiento de delegación, continuidad social y cuarta gestión, reintentos y concurrencia.
- Ensayo concurrente en MySQL: tres solicitudes simultáneas por cada origen dejan una atención, una actividad y dos compromisos en total.
- Navegador con base QA independiente: atención y actividad generaron un compromiso cada una, reutilizaron datos, mostraron navegación de ida/vuelta y admitieron reintentos sin duplicar. Sin errores JavaScript observados. Vista móvil de 390 px sin desbordamiento horizontal.
- Comprobación de Django y migraciones coherentes, sin cambios de modelo pendientes.

[Resultado de regresión](pruebas-locales.txt) · [Formulario escritorio](formulario-escritorio.png) · [Formulario móvil](formulario-movil.png).

Las pruebas locales usan datos ficticios y no acreditan todavía la ejecución de este flujo en AWS.
