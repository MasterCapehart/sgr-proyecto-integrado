# Clasificación y elegibilidad — incremento local

Estado: desplegado y verificado en AWS el 21/10/2026. Versión de aplicación `ed1e8759d86e9ea78f2c5a5a49610fa961b28125`.

Acceso: [Clasificación de actividades en AWS](https://54.236.112.203/pages/clasificacion-actividades.html).

## Dónde probar

- **Administración → Clasificación de actividades**: administrador y delegado pueden publicar nuevas versiones. Para funcionario con permiso de lectura aparece en **Catálogos de consulta**.
- Cada tipo de actividad (ÍtemMeta, ya utilizado en la captura) tiene una regla para la delegación activa. No se crea un catálogo paralelo ni se infiere la clasificación por palabras del nombre o la descripción.
- **Mi planilla → Registrar actividad o atención**: al seleccionar el tipo, se consulta al servidor una vista previa de clasificación y elegibilidad.
- **Detalle del registro**: muestra clasificación, motivo de exclusión y versión capturada.

## Reglas implementadas

| Condición | Resultado |
| --- | --- |
| Coordinación | No elegible para puntaje. |
| Otra gestión | No elegible para puntaje. |
| Ejecución no habilitada como válida | No elegible para puntaje. |
| Ejecución habilitada, con nombre y teléfono válido | Potencialmente puntuable; no se otorgan puntos. |
| Falta nombre o teléfono válido | Se conserva el registro, sin candidatura. |
| Beneficiario es el delegado | Clasificación efectiva Otra gestión; sin candidatura. |
| Tipo sin regla configurada | Sin definir; sin candidatura por defecto. |

Administrador y delegado mantienen el catálogo, mediante permiso explícito. Cada publicación exige motivo y control de versión. Las reglas se limitan a la delegación activa; la configuración de una delegación no afecta a las otras.

El origen interno/externo es independiente. Los hitos siguen siendo planificación; no se convierten en actividades puntuables por sus avances.

## Identificación y datos

El beneficiario municipal se selecciona explícitamente. También se detecta una coincidencia exacta de RUN con un delegado autorizado de la delegación, normalizando formatos con y sin puntos. No se confunde autor, profesional ni responsable de seguimiento con beneficiario. No se infiere identidad por coincidencia de nombres.

La condición de delegado y la regla usadas quedan capturadas. Los nombres y teléfonos ausentes se conservan vacíos; no se inventan datos para completar el formulario. La validación preliminar del teléfono exige formato admitido y entre 8 y 15 dígitos; los formatos malformados siguen siendo rechazados por la captura.

Al continuar un expediente social se reemplazan los datos del contacto y se recalcula la vista previa, sin reutilizar el teléfono de otra persona. Una atención social asociada conserva la misma evaluación del registro de actividad. Una atención independiente sin tipo de actividad permanece sin regla habilitante.

## Historia y límites de alcance

- Las reglas publicadas son versiones nuevas; no se editan ni eliminan versiones anteriores.
- Una actividad conserva la regla usada al capturarse. Editar su texto no la cambia a la regla vigente; corregir nombre o teléfono recalcula las condiciones con su regla capturada.
- Cambiar el tipo de actividad en un borrador aplica una nueva captura de regla para el tipo elegido y deja auditoría del cambio.
- Los registros anteriores sin evaluación capturada se muestran como **Sin evaluación histórica**. No se reclasifican automáticamente.
- Se conserva la estructura de las exportaciones de planillas. La evaluación detallada se consulta en la ficha del registro.
- No incluye puntajes efectivos, consolidación por revisión, límite diario, regla de tres días, tope120 %, felicitaciones ni ajustes de metas. Esos bloques permanecen separados.
- Migración aditiva `0024_clasificacion_elegibilidad`; no elimina registros ni importa clasificaciones por nombres.

## Validación

Suite completa:473 pruebas, OK, con un fallo esperado ya marcado. Doce pruebas específicas de este bloque aprobadas, incluyendo aislamiento y reintentos del catálogo, RUN formateado, historia, beneficiario delegado y seguimiento sin nombre.

Navegador local: publicación de regla, vista previa de ejecución, exclusión del delegado beneficiario, cambio de expediente sin reutilizar teléfono, guardado sin nombre/teléfono, detalle de motivos y vista móvil. Revisión independiente realizada; corregidos los casos de RUN formateado y vista previa tras cambiar de expediente.

## Despliegue AWS

Respaldo previo de archivos, configuración y base de datos; copia SQL cifrada en S3. Migración `0024_clasificacion_elegibilidad` aplicada y sin pendientes. Salud, versión y hashes de archivos verificados; servicios SGR y Nginx activos.

Pruebas autenticadas con administrador, delegado y funcionario: consulta del catálogo, edición disponible solo para gestores, API de publicación rechazada para funcionario, vista previa sin datos no elegible, captura con nombre y teléfono opcionales, registros históricos sin reclasificación automática y vista móvil. No se publicaron reglas ni se crearon actividades de prueba en AWS.

El catálogo debe configurarse explícitamente por administrador o delegado en cada delegación; el despliegue no habilita tipos por su nombre ni otorga puntos efectivos.
