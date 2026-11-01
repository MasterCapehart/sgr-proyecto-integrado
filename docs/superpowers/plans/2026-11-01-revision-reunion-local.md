# Revisión de la reunión: implementación local

**Objetivo:** resolver los cambios verificables de la transcripción del 1 de noviembre sin desplegar en AWS.
**Arquitectura:** conservar API, permisos y datos históricos; ampliar contexto de evidencias y aclarar estados independientes; ordenar compromisos antes de paginar. Directorios, calendario, reglas e indicadores se verifican con pruebas existentes y recorridos locales.
**Tecnologías:** Django, MySQL/SQLite aislado, HTML/CSS/JavaScript.
**Especificación:** transcripción aportada el 1/11 y desglose aprobado en el chat.

- [x] Evidencias: incluir solicitud y acción realizada en listado/detalle y explicar decisión disponible o bloqueada. Probar revisor sin permiso de consulta de actividades de equipo, revisión parcial y final, actualización y autoría.
- [x] Tubo: ordenar vencidas abiertas primero; luego Ingresado/Pendiente/En proceso; Realizado al final. Mismo orden en páginas/exportación; resaltar atraso.
- [x] Comunidad: comprobar pertenencias Integrante/Dirigente desde vecino y organización; hacer visible vínculo en listados y alta/edición sin duplicarlo como texto libre.
- [x] Clasificación: distinguir falta de configuración de actividad excluida y de confirmación de guardado. Facilitar acceso al catálogo autorizado, sin inventar reglas o reescribir evaluaciones históricas.
- [x] Fechas y vecinos: probar fechas posteriores de compromiso, validación clara y búsqueda/selección/duplicados; corregir defectos demostrados.
- [x] Ausencias, metas, colectivo: ejecutar pruebas y recorrido con datos ficticios; verificar aislamiento de delegación, ajuste proporcional y colores.
- [x] Preparar vista local autenticada con cuentas ficticias, accesos directos y matriz de resultados.

**Límites:** no reducir requisitos de contraseña; no introducir fórmulas nuevas ni habilitar todos los ítems para puntuar; aprobar una evidencia no cierra un compromiso. La simplificación social y los requisitos transaccionales anunciados se registran como pendientes de especificación; no se inventan. No modificar PPT, diagramas o documentos de entrega sin cambio concreto confirmado. No desplegar hasta nueva instrucción.


## Resultado de la revisión local

- Evidencia con contexto de actividad y acción realizada; historial y datos técnicos separados. No se amplía el permiso de consulta de actividades para poder revisar.
- Corregida respuesta obsoleta después de revisar el último respaldo: ahora devuelve actividad Validada. Aprobación parcial mantiene Pendiente y muestra el número de respaldos restantes.
- Tubo ordenado antes de paginar y exportar; atraso destacado, realizados al final.
- Vecino muestra organizaciones y rol; vínculo accesible desde listado y ficha. Al crear vecino u organización abre su ficha para vincularlo. No se duplican relaciones en texto libre.
- Búsqueda vecinal al escribir; fecha de compromiso respeta el mínimo sin impedir fechas posteriores.
- Confirmación de guardado separada del aviso de clasificación; acceso al catálogo autorizado. Filtro y contador de tipos sin configuración. No se han inventado ni habilitado reglas reales.
- Corregido cambio de delegación/cierre de sesión cuando falta el componente de borradores. Probado en Indicadores colectivos entre dos delegaciones.
- Calendario: 20 días previstos menos 1 ausencia = 19 disponibles; meta 10 ajustada a 9,5. Con una actividad válida: 10,53 %. Comprobado en pantalla.
- MySQL local aislado: 625 pruebas, 624 correctas y 1 fallo esperado preexistente; detalle en .integracion/reunion-local/regresion-completa.txt. Sin AWS.
- Recorridos reales del navegador local: evidencia parcial/final, tubo, vecino dirigente, filtro de clasificación, metas y cambio de delegación.

## Por confirmar con el cliente, no implementado por suposición

- Definición autorizada de los tipos de actividad que aún no tienen regla; los avisos son correctos mientras falte definición. Las reglas ficticias de la demo no se trasladan a producción.
- Qué documento o pantalla social se desea resumir y qué información conservar.
- Si la observación sobre contraseñas pide únicamente instrucciones de evaluación; no se reduce la seguridad ni se cambia ninguna contraseña.
- Documento transaccional anunciado por la docente, todavía no entregado.

**No desplegado.** Copia de demostración: http://127.0.0.1:8031/revision-local/ . Su acceso directo de perfiles es exclusivo del servidor local privado y no forma parte del producto.
