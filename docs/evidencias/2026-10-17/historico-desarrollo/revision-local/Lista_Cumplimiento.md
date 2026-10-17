# Lista de cumplimiento local — incremento y operación

Fuente: Requisitos_y_Plan_Pruebas_Segunda_Evaluacion_SGR.pdf, 32 páginas.
Alcance autorizado: copia `sgr-eva2-local`, acceso, mantenedores, atención, permisos,
auditoría, actividades, evidencias, agenda, revisión y conversación con datos reales. Este archivo es la lista de trabajo del punto 1;
no es el informe de cierre B21 ni aprueba los 84 casos completos del documento.

## Lista comprobable

| Requisito / referencia | Función o pantalla | Comprobación | Estado y límite |
|---|---|---|---|
| A1, ACC-01 | Login por usuario/correo | Suite core y navegador con Administrador, Coordinador, Delegado, Funcionario D01/D02, Verificador y Consulta | Comprobado en QA local; permisos mínimos de prueba, pendientes de aceptación funcional |
| A3, ACC-02/03 | Rechazo de credenciales, cuenta/rol inactivo, cierre de sesión | Pruebas de backend; límites persistentes por cuenta/IP | Comprobadas las variantes registradas; no equivale a aprobar todo el plan de seguridad |
| A1/A3, ACC-04/05/06 | Solicitar, verificar, reenviar, vencer y consumir código; nueva clave | Suite core y recorrido de recuperación en navegador | Funciona con buzón privado local; SMTP externo aplazado |
| A2, ADM-06 | Nombre/rol/código y nombre de delegación permanentes | Prueba de perfiles y rechazo de cambio a ámbito ajeno | Comprobado; contexto fijo con una delegación y selector con varias autorizadas |
| A1, ADM-01/02 | Delegaciones | Crear, consultar, editar, cancelar, activar/desactivar; código/nombre únicos y relaciones | Comprobadas variantes de A1; sin padrón ni jurisdicción inventada |
| A1, ADM-03/04 | Roles y usuarios | CRUD, correo/usuario/clave válidos, ámbito autorizado, sin escalamiento | Comprobadas variantes de A1; administración de cargos es alcance distinto |
| A1, CAT-01 | Ítems y metas | CRUD del catálogo de ítems; impedir baja con configuración activa | Catálogo operativo; no se presenta un motor de indicadores completo |
| A1/A2, CAT-02/03 | Tipos y subatenciones | CRUD, padre activo y relaciones protegidas | Comprobado en API y pantallas; no reactivar hijos con padre inactivo |
| A1/A3, CAT-05/06 | Seis mantenedores | Vacíos, longitudes, duplicados, formato, relaciones, consulta sin guardar y cancelación | Suite y recorrido real; campos opcionales conservan las reglas del modelo |
| A2, UX-01/02 | Búsqueda, filtros, orden, páginas y total | Filtro parcial en minúsculas; 23 registros en tres páginas; sin omisiones | Comprobado en Chrome for Testing y Edge |
| A2, UX-03 | XLSX del filtro completo | Archivo abierto con openpyxl; 23 identificadores únicos, sin password/tokens/versión interna | Comprobado para el escenario; el resto de exportaciones se comprueba por la suite y CRUD |
| A1/A2/A3, ACT-05/06 | Atención ciudadana | Cambio de tipo limpia subatención; cancelar conserva el total; doble clic produce un POST y una atención | Comprobado con navegador y base real de la copia |
| A2/A3, SEG-01/02 | Permisos y aislamiento territorial | Peticiones directas sin autorización y acceso a otro ámbito | Rechazos comprobados; no es un pentest ni certificación completa de seguridad |
| A3, UX-04 | SweetAlert2 y estados reales | Error 503 controlado, duplicado, advertencias, éxito tras persistir | No se sustituyen fallos por datos simulados; formulario inválido conserva datos |
| B15, INT-02 | Edición simultánea de maestros | Versión leída obligatoria; rechazo 409 de editor obsoleto | Implementado en los siete recursos editables; atención permanece inmutable |
| B15, INT-03 | Auditoría de eventos implementados | Actor, fecha, origen, contexto, acción y antes/después; consulta restringida e inmutable por API | Ampliada; los eventos antiguos no se rellenan inventando valores |
| A2, D (p. 32) | Identidad gráfica | Arial, acento #AD0000, activo municipal conservado y espacio alrededor | Alineado con el PDF; no se afirma aprobación institucional |
| UX-05 | Accesibilidad | Etiquetas, abrir por teclado, Escape, retorno del foco, estado textual y contraste | Comprobadas las variantes registradas; tabla desplazable y enfocables sus controles |
| UX-06 | Chrome y Edge; escritorio y móvil | Chrome for Testing y Edge; 1440×1000 y 390×844, sin desborde de página | Versiones y capturas en resultados técnicos privados |

## Permisos de prueba y sus límites

- Administrador: mantenedores y auditoría. Cuenta de prueba existente `admin.local`.
- Coordinador: operación y consulta de equipo en D01/D02; auditoría.
- Delegado: operación de equipo en D01.
- Funcionario F01/D01 y F02/D02: registros propios, archivos propios, atención, conversación y lectura de agenda de su unidad. Solo edita compromisos propios o asignados.
- Verificador: consulta de equipo y revisión de evidencias ajenas de su delegación; no aprueba las propias.
- Consulta: lectura de equipo dentro de la delegación autorizada, sin modificar registros.

Son propuestas conservadoras basadas en los actores de S1 y los datos del plan B2.
La matriz institucional definitiva necesita aprobación del equipo/responsable funcional.
Credenciales: `.aislamiento/cuentas-locales.json` y `.aislamiento/perfiles-revision.json`.
No incluir esos archivos en Git ni en documentación pública.

## Detalles de las correcciones

- Se volvió a `#AD0000`, indicado en la página 32 del PDF recibido.
- Los cambios sobre maestros requieren `_version` igual a la versión consultada. Si falta,
  la API devuelve 428; si fue modificada, 409. La interfaz conserva el formulario y solicita
  recargar. No se reintenta sobrescribiendo automáticamente.
- El panel técnico Django se dejó en consulta para evitar saltarse la validación, la versión
  y la auditoría de la API.
- Auditoría de altas, ediciones, estados, atención, cambios de contexto, acceso/salida,
  cambios de contraseña y exportaciones. Contraseñas, hashes y códigos quedan excluidos
  de las instantáneas. El cambio de clave solo conserva metadatos de renovación.
- Datos históricos incompletos se identifican como tales; no se fabricó su antes/después.
- Persistencia de fechas en UTC; presentación mediante fecha local del navegador, en español.

## Resultados técnicos para reproducir la revisión

Se guardan en `.revision-local/` (privado), sin actualizar el informe anterior:

- `backend.log`: ejecución completa de la suite.
- `navegadores.json`: versiones, perfiles y variantes de interfaz comprobadas.
- `crud-ui.json`: recorridos de los seis mantenedores.
- `recuperacion-ui.json`: recuperación mediante buzón local y acceso con la nueva clave.
- `atencion-auditoria.json`: cancelación, dependencia de catálogos, doble envío y auditoría.
- `chrome-filtro.xlsx`, `edge-filtro.xlsx`: exportaciones de 23 registros ficticios.
- Capturas de escritorio y móvil.

Comandos desde la raíz de la copia:

```bash
backend/.venv/bin/python backend/manage.py test core --noinput
node scripts/revisar_entrega_local.cjs
backend/.venv/bin/python scripts/comprobar_aislamiento.py
```

Las pruebas de navegador necesitan los servicios iniciados y crean datos ficticios en esta
copia. Las pruebas Django usan exclusivamente `test_sgr_eva2_local`.

## Fuera de esta ejecución

- Punto 5: no actualizar diagramas ni preparar/actualizar el informe final de pruebas.
- GitHub, publicación de commits/PR, SMTP externo y AWS.
- Carga/estrés del despliegue, aprobación humana y certificación municipal.
- Módulos futuros de agenda, evidencias, cálculo, tableros y colaboración.

Los diagramas, el manifiesto y el informe anteriores describen la versión anterior y
necesitarán actualizarse cuando se autorice el punto 5. Ninguna exclusión se cuenta como
requisito de la entrega completa aprobado.


## Ampliación operativa — 15 de octubre de 2026

| Fuente / módulo | Implementado | Evidencia real |
|---|---|---|
| Guía SGR RF-009/010/011 | Actividad con fecha, solicitud, acción, contacto, teléfono, sector, ítem, autor y código único inmutable; control de versión | `core.test_domain`; creación y consulta en Chrome/Edge |
| RF-012/013 | PDF/PNG/JPEG privados, nombre, tamaño, SHA-256, vínculo a actividad, versiones devueltas e historial | Descarga autorizada; rechazo de HTML y de descarga desde otra delegación; reemplazo conservando revisión |
| RF-013/014 | Revisión ajena: aprobar/rechazar/corregir con autor, fecha y observación; estado de actividad según respaldos vigentes | Revisor distinto en navegador; autoaprobación bloqueada; no genera puntuaciones |
| RF-016/017/018 | Compromiso con solicitante, sector, responsable autorizado, fecha, área y origen; estados controlados; reprogramación y reasignación con historial | Creación y seguimiento desde interfaz; antes/después auditados |
| RF-019/032 | Agenda por fecha; filtro de estado, responsable, sector y fechas; filtro de vencidos/hoy y etiqueta de vencimiento | API y controles reales; no se define un umbral institucional de proximidad no documentado |
| RF-033/035/036 | Reportes XLSX de filtros; conversación con contexto único; auditado de creación/edición/revisión/comentarios | Excel descargado en Chrome/Edge; mensajes persistidos; restricciones de ámbito |
| M01–05, M08–20 | Encabezado, escudo, Arial, rojo #AD0000, menú por grupo, tablas, formularios, ficha de compromiso y conversación | CSS y escudo proceden de Mockups_SGR; JS de simulación no se copió |
| M06–07 | Se retiran métricas ficticias; se informa que el motor de cálculo está excluido | No se presentan porcentajes como resultados reales |
| Ítems y metas | Se agrega acceso a configuración de metas por ítem/período | Creación real desde interfaz; corrección de colisión del campo `item` con `form.elements.item` |

### Pasadas de verificación

1. Contraste del alcance con PDF de segunda evaluación, guía SGR y fuentes de Mockups_SGR.
2. Backend: 154 pruebas aprobadas en MySQL de prueba; incluye 15 nuevas de dominio.
3. Chrome: actividad → comentario → archivo → revisión por otra cuenta; compromiso → seguimiento → mensaje; exportación.
4. Edge: repetición del mismo recorrido con persistencia real.
5. Revisión visual: escritorio/móvil, contexto visible, ficha en dos columnas, seis CRUD existentes, atención y auditoría. La prueba visual detectó y permitió corregir el selector `item` de metas.

Resultados técnicos privados: `.revision-local/backend-operacion-final.log`, `operacion-ui.json`,
`navegadores.json`, `crud-ui.json`, `atencion-auditoria.json`, `revision-visual.json` y capturas.
Scripts reproducibles en `scripts/verificar_operacion_ui.cjs` y `scripts/revisar_vistas_operativas.cjs`.

### Límites explícitos

No acredita el 100% del plan completo de 84 casos ni aprobación municipal. Cálculos de desempeño,
ponderación aplicada, semáforos derivados, AWS y correo externo están excluidos.
Recuperación funciona con el buzón privado local. Permisos QA son propuestas para pruebas,
no una matriz institucional aceptada. El límite de archivos de 10 MB y los formatos PDF/PNG/JPEG
son la política técnica de este avance local. No se modifican diagramas ni informes de cierre anteriores.

### Revisión independiente final

Se corrigieron dos hallazgos verificables antes del cierre local:

- Observación no textual en seguimiento: prueba reprodujo HTTP 500; ahora devuelve 400 y conserva estado/versión. Incluida en las 154 pruebas aprobadas.
- Reportes con permisos parciales: prueba de navegador reprodujo bloqueo; ahora elige un recurso autorizado aunque el perfil no pueda consultar actividades. Resultado en `.revision-local/reporte-permisos.json`.

La revisión no es una certificación de seguridad ni acredita funciones excluidas.


## Acercamiento a los Excel municipales — 15 de octubre de 2026

Referencia: diez imágenes de `Galería-20260831`. No se importaron datos personales de las fotografías.

| Elemento de las planillas | Cambio aplicado | Verificación |
|---|---|---|
| Funciones y áreas de los funcionarios | Catálogo Cargos y áreas; asignación en Usuarios; cargo independiente del rol; ítems generales o por cargos | Pruebas de asignación sin cambio de permisos y de rechazo/ocultación de ítems ajenos; recorrido Chrome/Edge |
| Gestiones | Columnas de fecha, solicitud, acción, contacto, teléfono, tubo, ítem, derivación, código y respaldo; cargo y funcionario | Registro real desde interfaz y comprobación de cargo capturado |
| Tubo de trabajo | Fecha de solicitud independiente, origen INT/EXT, territorio, responsable, compromiso, mes derivado de su fecha, apoyo, observaciones y estado | Creación real, vínculo desde actividad y consulta; no se inventan fechas antiguas |
| Derivado a | Destino, motivo, estado de derivación y registro de autor/fecha en historial; versión y auditoría | Derivación real y rechazo de una versión obsoleta |
| Evidencia verificadora | Archivo vigente y estado visibles en la fila de gestión; descarga protegida | Archivo PDF adjuntado desde interfaz y enlace visible |
| Tres gestiones sociales | Expediente único, primera/segunda/tercera gestión; RUN, teléfono, visita, informe, beneficio y observaciones; responsable y clasificación visibles | Tres registros desde la interfaz en ambos navegadores; máximo de tres conservado |
| Campos históricos desconocidos | Fechas vacías; requiere visita desconocido en registros anteriores a la incorporación del campo | Pruebas y migración 0013; no se presenta un No sin ese antecedente |
| Operación semejante a Excel | Encabezados/primeras dos columnas fijos; filtros de columna y limpieza de filtros; XLSX con títulos legibles, ajuste de texto y paneles fijos | Chrome/Edge, primera columna fija comprobada por posición; archivos abiertos con openpyxl |
| Fechas locales | Calendario operativo America/Santiago; almacenamiento de instantes con USE_TZ | Prueba de una hora UTC que todavía corresponde al día anterior en La Serena |

Para configurar funciones reales: crear los cargos en Cargos y áreas, asignar el cargo a cada cuenta
en Usuarios y seleccionar sus cargos aplicables en Ítems y metas. No se dedujeron cargos a partir de
los roles existentes. Los ítems sin cargos son generales. Las cuentas sin cargo solo usan ítems generales.

La columna «Unidad» de las fotografías no se interpretó como cantidad ni como unidad organizacional
porque las imágenes no definen su significado. Los cálculos, ponderaciones aplicadas y semáforos siguen excluidos.

Pruebas reproducibles: `backend/core/test_excel_workflow.py` y `scripts/verificar_excel_workflow.cjs`.
Resultados privados: `.revision-local/excel-suite-final.log`, `excel-workflow-ui.json`,
`excel-regresion-navegadores.log`, `excel-regresion-crud.log`, `excel-aislamiento.json`, capturas
`*-excel-gestiones.png`, `*-expediente-social.png`, `*-expediente-movil.png` y XLSX comprobados.
La revisión independiente detectó dos problemas corregidos con pruebas: ítems exclusivos ofrecidos a
cuentas sin cargo y error 500 al reintentar una atención con datos sociales inválidos. También se
verificó JSON inválido, repetición con RUN formateado y filtros por nombre completo/usuario.

Resultado final de esta ampliación: **171 pruebas de backend aprobadas**; recorridos nuevos y regresión en Chrome/Edge aprobados. Los límites de cálculo, AWS y correo externo permanecen vigentes.


## Cierre local 15-10-2026

Se implementaron historial de catálogos, borradores, reglas y permisos revisables, alertas, cierre tardío y anulación auditable. Evidencias: [Informe del cierre](cierre-local/Informe_Cierre_Local.md). 184 pruebas de backend y 46 comprobaciones de navegador aprobadas. No implica aceptación humana ni cobertura integral de los 84 casos del documento. AWS, publicación y cálculos permanecen aplazados.
