# Fichas corregidas SGR

Revisión: 2026-10-17T11:32:34-03:00. 14 métodos de servidor aprobados y 222 comprobaciones. Acceso verificado con seis perfiles en navegador.
No equivale a aprobación integral del sistema. Las fichas explican las verificaciones pendientes.

## Ficha_Prueba_ACC01_Roles_Completa.docx
Aprobado en las variantes ejecutadas. No acredita que la matriz de permisos haya sido aceptada por el municipio; comprueba las asignaciones de las cuentas QA.

## Ficha_Prueba_ACC02_ACC03_Seguridad_Acceso.docx
Aprobado en las variantes ejecutadas. Las variantes de usuario vacío y contraseña vacía se ejecutaron por separado en el servidor; la captura del formulario corresponde a ambos campos vacíos.

## Ficha_Prueba_ACC04_ACC05_ACC06_Recuperacion.docx
Aprobado en servidor controlado y pendiente de aceptación integral. Falta repetir y registrar el recorrido completo en navegador con un correo real recibido por Gmail y la confirmación SweetAlert2 del cambio. La recepción anterior informada por el usuario no sustituye esa evidencia integral. El servidor bloquea el reenvío anticipado con HTTP 429; no se afirma que el botón permanezca deshabilitado durante la espera.

## Ficha_Prueba_ADM06_Contexto_Delegacion.docx
Cobertura parcial del caso. Se comprobaron selector y cambio de contexto por servidor. Falta registrar el cambio autorizado en la cabecera y el aislamiento de datos de cada listado, además del tratamiento de un formulario con cambios sin guardar.

## Ficha_Prueba_CRUD_Delegaciones_ADM01_ADM02.docx
Cobertura parcial de los casos. CRUD, duplicados, relaciones, búsqueda, paginación y Excel aprobados en servidor. Falta comprobar la aparición inmediata en todos los selectores de asignación y la cancelación de desactivación desde la interfaz. La baja con relaciones se bloqueó; no se declara aprobada una desactivación de D01 con actividades.

## Ficha_Prueba_CRUD_Usuarios_ADM03.docx
Aprobado en servidor y pendiente de interfaz completa. CRUD, asignaciones y rechazo de cuenta inactiva comprobados. Falta registrar el ciclo visual completo y la cancelación de operaciones; esta ficha no presenta las capturas históricas como ejecución nueva.

## Ficha_Prueba_CRUD_Roles_ADM04.docx
Aprobado en servidor y pendiente de interfaz completa. CRUD, lectura permitida, escritura denegada y protección de roles vinculados comprobados. Falta registrar el ciclo visual completo y sus confirmaciones.

## Ficha_Prueba_CRUD_ItemsMetas_CAT01.docx
Cobertura parcial del caso. Se probó el CRUD del ítem y la restricción por configuración activa. Falta comprobar vigencia temporal y conservación de referencias de períodos cerrados. No se ejecutó el CRUD de configuraciones de metas ni cálculos; no se declara cobertura de ambos por haber probado el catálogo.

## Ficha_Prueba_CRUD_Tipos_Subatenciones_CAT02_CAT03.docx
Aprobado en servidor y pendiente de interfaz completa. Se probó cada catálogo, el cambio de tipo padre y el rechazo de relaciones inválidas o inactivas. Falta registrar la actualización visual del selector dependiente y verificar específicamente la conservación de atenciones históricas al cambiar el catálogo.

## Ficha_Prueba_Ingreso_Atencion_ACT05_ACT06.docx
Aprobado en servidor y pendiente de interfaz completa. La cuarta gestión se rechazó con HTTP 409 y el reintento conservó un solo folio. Falta registrar doble clic real en navegador, cancelación del formulario y visualización final del folio y contexto. Un envío simple no se considera evidencia de doble clic.

## Evidencias
Conservar ../evidencias_fichas_corregidas junto a estos documentos. JSON, registros, capturas y seis exportaciones verificadas.
Las dos fichas anteriores de ACC01 son antecedentes históricos y están identificadas como sustituidas.
Respaldo previo: ../respaldo_fichas/20261017_111806.
