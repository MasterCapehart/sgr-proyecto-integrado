# Revisión visual contra los ejemplos del documento

Fuente: Requisitos_y_Plan_Pruebas_Segunda_Evaluacion_SGR.pdf, páginas 26–32 (C1–C6 y D). Revisión de páginas renderizadas, capturas nuevas de la aplicación local y marcado de recuperación. No se modificó código de aplicación.

## Conclusión

La base visual es coherente con las referencias: cabecera roja, identidad y delegación permanentes, tipografía Arial, fondos claros, acción de creación, búsqueda, exportación y selección dependiente Tipo/Subatención. Esto no certifica usabilidad con usuarios ni conformidad integral del manual de marca. Los ejemplos académicos no constituyen aprobación institucional.

## Hallazgos y propuesta

| Prioridad | Hallazgo observado | Mejora propuesta |
|---|---|---|
| Alta | Administrador tiene 19 accesos contando Inicio. Consulta y control está dividido en dos grupos. | Reunir en Inicio, Gestión diaria, Seguimiento y Administración; desplegables y sin numeración global. Conservar permisos. |
| Alta | Registrar atención sitúa aviso técnico y cuatro KPI antes del formulario; Guardar queda más abajo. El PDF C6 presenta directamente la tarea. | Formulario primero, resumen en pestaña o sección secundaria, información automática breve y acciones siempre fáciles de encontrar. |
| Alta | Usuarios muestra nueve columnas y correo cortado en varias líneas; acciones hacia el borde requieren desplazamiento. El PDF C4 prioriza nombre, correo, rol y delegación. | Mostrar nombre completo, correo, rol, delegación, estado y acciones; usuario/cargo/datos adicionales en detalle o columnas configurables. No eliminar datos del modelo. |
| Media | Todas las acciones por fila son enlaces rojos con peso similar. | Distinguir Ver/Editar y agrupar Historial/Desactivar en Más acciones, manteniendo confirmación y acceso por teclado. |
| Media | Avisos extensos explican servidor, inmutabilidad y secciones de la guía. | Mensajes operativos breves; detalles técnicos en ayuda. |
| Media | Inicio ofrece tarjetas de módulos pero no destaca una tarea principal según el perfil. | Acciones directas como Registrar atención y Consultar pendientes; KPI con enlaces a filtros reales cuando corresponda. |
| Media | El login mantiene un vínculo a Guía de componentes. | Retirar ese acceso del flujo de trabajo final y mantenerlo solo en documentación técnica. |
| Por validar | C2 describe seis casillas y navegación entre ellas; validar-codigo.html utiliza un único campo de seis dígitos. | Alinear la presentación y verificar pegado completo, teclado, foco y lectura accesible. No afirmar que esta revisión visual volvió a ejecutar el restablecimiento. |

## Qué conservar

Color y marca actuales, contexto de sesión, validaciones de servidor, permisos, SweetAlert2, persistencia, exportación y la adaptación móvil ya implementada. Los KPI son una ampliación; no deben desplazar las tareas que los mockups ponen en primer plano.

## Alcance de la revisión

Se inspeccionaron las siete páginas completas de referencia (once diseños y normas), capturas actuales de login, recuperación, Inicio, los seis mantenedores obligatorios, registro de atención, actividades y agenda. C2 se contrastó con el HTML actual; no se solicitó ni consumió un código nuevo, ni se modificaron contraseñas. No hubo pruebas de usabilidad con personas ni cambios de diseño en esta revisión.

Las capturas y el inventario de menú/columnas se conservan en `.revision-local/comparacion-mockups/`. No se publicaron datos ni se modificó el proyecto original.
