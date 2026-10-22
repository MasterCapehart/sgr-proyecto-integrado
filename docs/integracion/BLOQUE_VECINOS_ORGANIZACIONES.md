# Vecinos y organizaciones — incremento local

Estado: desplegado y verificado en AWS. Versión de aplicación `1387aa8a976d802588fcb1e173b3bf50db1664f6`.

## Dónde probarlo

En el menú **Comunidad** de [SGR](https://54.236.112.203/index.html):

- **Vecinos**: registrar, consultar y editar datos; desactivar o reactivar según permiso.
- **Juntas y organizaciones**: datos comunitarios y legales, territorio, socios activos y pertenencias.

Desde la ficha se vinculan vecinos y organizaciones. Un vecino puede pertenecer a varias organizaciones y ser **Integrante** o **Dirigente** en cada una. Cada pareja tiene un vínculo único, reactivable; las desactivaciones requieren motivo y conservan historial.

En **Registrar gestión**, al seleccionar un vecino se muestran sus organizaciones activas. La selección de la organización relacionada es opcional y conserva su nombre como referencia de esa gestión.

## Permisos iniciales

| Perfil existente | Vecinos | Organizaciones y pertenencias |
| --- | --- | --- |
| Funcionario | Consultar, registrar y editar | Consultar |
| Delegado / Administrador | Consultar, registrar, editar y desactivar/reactivar | Gestionar |

La migración agrega permisos explícitos a los roles canónicos existentes sin eliminar los anteriores. Los demás roles personalizados no reciben ampliaciones automáticas. Cada consulta y modificación se limita a la delegación activa autorizada.

## Conservación e integración

- Migración aditiva `0022_organizaciones_pertenencias`; sin borrado físico.
- Los nombres y datos históricos de actividades se conservan aunque cambie el directorio.
- Los textos antiguos de juntas no se convierten automáticamente en organizaciones o pertenencias.
- El territorio del vecino utiliza el campo de sector existente; no se incorpora un catálogo territorial nuevo.
- Los datos legales desconocidos pueden quedar vacíos. Socios desconocidos y cero socios son valores diferentes.
- Los cambios utilizan versión para detectar ediciones simultáneas y dejan auditoría.

## Validación

Suite completa: 447 pruebas ejecutadas correctamente, con un fallo esperado ya marcado por la suite. Sin migraciones pendientes de generar.

33 pruebas específicas aprobadas: permisos, aislamiento entre delegaciones, versiones, duplicados, reactivación, datos y preservación del historial. Recorrido de navegador local aprobado: organización, vecino, vínculo como dirigente y uso en captura; comprobación móvil sin desbordamiento exterior.

No incluye hitos, motor de puntuación, ausencias ni indicadores colectivos de los siguientes bloques.

## Despliegue AWS

Aplicada la migración `0022_organizaciones_pertenencias`. Respaldo previo de archivos, configuración y base de datos; copia SQL cifrada en S3. Salud, versión y hashes de los archivos verificados; servicios SGR y Nginx activos.

Comprobación autenticada de administrador, delegado y funcionario: directorios y menú disponibles; el funcionario puede registrar vecinos y consultar organizaciones, pero no crear organizaciones (API responde403 y el botón no aparece). No se crearon registros comunitarios de prueba en AWS durante esta comprobación.
