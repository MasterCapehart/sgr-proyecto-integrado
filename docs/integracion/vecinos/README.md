# Vecinos en la captura de trabajo — 21/10/2026

## Funcionamiento

Mi planilla → Registrar actividad o atención → **Buscar vecino registrado**. Se busca por al menos tres letras del nombre o RUN completo. Los resultados pertenecen a la delegación activa y muestran nombre, RUN informado, sector y junta. La búsqueda devuelve hasta 20 coincidencias; no proporciona un listado global ni exportación.

Si no existe, **Registrar vecino** abre un formulario con nombre obligatorio y RUN, teléfono, sector y junta opcionales. Guardar registra el vecino y permite usar sus datos sin crear aún una actividad. El vecino se puede reutilizar en capturas posteriores. Un RUN informado se valida, normaliza (puntos, guion, mayúscula de dígito K y ceros iniciales) y no se repite dentro de la misma delegación. Homónimos sin RUN no se fusionan automáticamente.

Seleccionar completa nombre, RUN, teléfono, sector y junta. Nombre y RUN quedan protegidos mientras esté vinculada esa persona. Se puede quitar la selección y editar el contacto o elegir otra persona. Teléfono, sector y junta pueden ajustarse para la captura actual; eso no actualiza silenciosamente el directorio vecinal. No se incluye todavía una pantalla de edición del directorio.

Las actividades internas y contactos de organizaciones pueden registrarse sin crear ni seleccionar un vecino. El RUN de contacto se valida cuando se informa, también en actividades no sociales. Los expedientes sociales conservan el solicitante y el RUN; seleccionar una persona incompatible se rechaza y no reescribe el expediente. La actividad muestra el RUN capturado en su detalle.

## Persistencia, permisos y compatibilidad

Migración 0020: crea Vecino y agrega vínculo opcional protegido y RUN de contacto a Actividad. Los registros históricos no se convierten automáticamente en vecinos ni se importan personas desde el Excel. Las actividades conservan sus datos de contacto como captura histórica, junto con el vínculo opcional al directorio. La eliminación accidental de un vecino relacionado queda protegida.

Las rutas POST `/api/vecinos/buscar/` y `/api/vecinos/` requieren sesión activa, permiso de crear actividades y delegación autorizada. La búsqueda usa el cuerpo de la solicitud para no poner RUN/nombres en la URL. Las respuestas están acotadas a la delegación activa, incluso para administradores. No se asignan nuevos permisos a roles existentes.

El alta requiere una clave idempotente. La restricción RUN/delegación y la recuperación posterior a conflictos evitan duplicados o errores falsos ante reintentos. Nombre, RUN y campos de contexto se validan en servidor; no se acepta delegación o autor desde el navegador. La captura de actividad comprueba la referencia vecinal y la coherencia del nombre/RUN. La edición de actividades vinculadas conserva esa identidad. El alta vecinal queda auditada.

## Verificación local

12 pruebas nuevas: registro/búsqueda/reutilización, normalización y duplicados, permisos y ausencia de sesión, aislamiento entre delegaciones, referencia ajena, validaciones, búsqueda vacía y limitada, alta sin RUN, captura histórica del teléfono, coherencia social e identidad en edición, reintento confirmado entre consultas.

Regresión completa: **426 casos, 425 aprobados y un fallo esperado preexistente**. Navegador QA: buscar sin resultados, registrar vecino desde el formulario, completar los cinco datos, reutilizar por RUN, guardar captura general y social, y móvil sin desbordamiento. Revisión independiente de integridad y reintentos; hallazgos corregidos y comprobados antes del despliegue.

## Despliegue verificado — AWS personal

Publicado el 21/10/2026, aplicación `dc97a010889ad862f5a60b501bed18b25a165441`. [Abrir formulario](https://54.236.112.203/pages/registro-trabajo.html).

- Respaldo SQL previo de 2.767.564 bytes cifrado en S3 privado y copia de archivos/configuración de la versión anterior.
- Migración 0020 aplicada con credencial temporal de esquema; no se ampliaron permisos del usuario de la aplicación.
- 19 archivos verificados, salud y versión correctas; servicios SGR y Nginx activos.
- 41 comprobaciones remotas aprobadas: registro y reintento de vecino, duplicado de RUN, búsquedas por nombre/RUN, captura vinculada, conservación del directorio al editar datos de contacto de una captura, identidad protegida en edición, aislamiento entre delegaciones y rechazo de operaciones para Consulta, además del flujo social y del tubo. Todas las filas QA se revirtieron; los conteos finales coincidieron.
- Navegador con Administrador, Funcionario y Consulta: buscador de vecinos, formulario de alta, permisos y móvil. No se enviaron altas de negocio desde esta revisión del navegador; abrir la captura sí genera su reserva auditable de código.

El laboratorio no se modificó. No se importaron vecinos históricos ni personas del Excel. Los datos de un vecino se registran explícitamente desde el formulario.

[Evidencia de despliegue](aws-2026-10-21/despliegue.txt) · [Pruebas transaccionales](aws-2026-10-21/verificacion-transaccional.txt) · [Navegador AWS](aws-2026-10-21/navegador.json).
