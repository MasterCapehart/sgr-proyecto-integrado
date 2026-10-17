# Adaptación operativa local al Excel — 16-10-2026

Implementada exclusivamente en `sgr-eva2-local`. El archivo Excel y el proyecto original mantienen sus hashes de referencia. No se hizo commit, push ni despliegue. No se importaron nombres ficticios de trabajadores ni filas de ciudadanos del Excel. Las pruebas de interfaz crean únicamente fixtures identificados como QA en la copia local.

## Funcionalidad incorporada

- **Mi planilla de trabajo:** vistas General, AP ADM., COOR DISERCO, T OC, G SOC, PLAN y CON y GES SEG. Las columnas toman los rótulos de referencia; las columnas auxiliares de cálculo no se presentan como datos manuales. Cargo y rol siguen separados. En Cargos y áreas se puede elegir la planilla de una función; las cuentas se asignan mediante Usuarios. No se reasignaron trabajadores automáticamente.
- **Catálogos de referencia:** seis funciones genéricas y 25 ítems nuevos obtenidos de listas de la matriz. Los ítems se vinculan a su función. Las relaciones de Tipo/Subatención existentes se conservan: las listas independientes del Excel no se convierten en relaciones inventadas.
- **Gestión social:** tabla con primera, segunda y tercera gestión; fechas programada y realizada separadas; informe, beneficio y vínculo autorizado al tubo. Exportación XLSX de todos los casos filtrados. La fecha heredada conserva su valor sin atribuirle una clasificación que no se conoce. La ficha mantiene los registros por etapa, autor y fecha.
- **Tubo de trabajo:** rótulos y orden familiar; Unidad fija en 1 por registro, tal como se usa en la matriz; referencia de código de foto. Esta referencia no equivale a una aprobación automática de un archivo.
- **GES SEG:** profesional seleccionable entre cuentas configuradas de la delegación. No contiene responsables copiados de listas ficticias del Excel.
- **Reclamos y felicitaciones:** captura, consulta, edición versionada, filtros y exportación con permisos propios/equipo y delegación. Incluye profesional configurado, medio escrito y vínculo a evidencia privada; no puntajes simulados.
- **Diseño:** grupos desplegables únicos, nombres familiares, acciones directas de inicio, formulario de atención antes del resumen, columnas de Usuarios reducidas y acciones secundarias agrupadas. Código de recuperación con seis casillas visuales sobre un campo accesible que conserva pegado y edición con teclado.

## Verificación ejecutada

- **207 pruebas de backend aprobadas**, incluidas 15 específicas de la adaptación. Se verificaron fechas, tipo por etapa, vínculo a otra delegación rechazado, planilla no suplantable, conservación del perfil histórico, unidad fija, exportación segura y profesional configurado.
- **22 comprobaciones de adaptación en Chrome y Edge**: menú, vistas/exportación, tubo, fechas sociales, etapas, reclamos persistidos, acciones secundarias, móvil, código y selector profesional.
- **34 comprobaciones de regresión general** y **20 de KPI** aprobadas.
- **Dos recorridos completos de regresión operativa**, Chrome y Edge: cargo/ítems, actividad, derivación, evidencia, filtros, columna fija, exportación y tres gestiones capturadas desde la interfaz.
- Revisión independiente detectó y permitió corregir la edición al cambiar de cargo y la diferencia entre vista de consulta y planilla de captura. El recorrido rápido detectó un orden de carga de catálogos que dejaba la subatención deshabilitada; se habilita el formulario al terminar de cargar sus dependencias.

Los registros de ejecución están en esta carpeta. Ninguno de estos resultados equivale a aceptación humana de todos los casos del PDF o a equivalencia matemática del Excel.

## Uso

1. Entrar a http://127.0.0.1:8010.
2. Abrir **Mi planilla de trabajo**, **Tubo de trabajo**, **Gestión social** o **Reclamos y felicitaciones**.
3. Para configurar funciones, abrir **Administración → Cargos y áreas**, elegir la planilla del cargo y asignarlo a una cuenta ya configurada desde **Usuarios**. No hace falta crear un trabajador por cada hoja numerada del Excel.
4. La exportación conserva la vista de columnas elegida o la estructura social de tres etapas; no se limita a la página visible.

## Alcance pendiente conservado

El motor ponderado de SALON/SEMAFORO/RESUMEN, la validación matemática de fórmulas originales, AWS, publicación y correo externo continúan aplazados según las instrucciones del usuario. CARTAS y las hojas ocultas de apoyo no se activan como módulos nuevos por su sola presencia. Los perfiles y transiciones institucionales requieren aceptación funcional; no se registra una aprobación humana ficticia.

[Vista de planilla](planilla.png) · [Atención en móvil](atencion-movil.png) · [Tres gestiones](tres-gestiones.png).
