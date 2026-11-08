# DA06 · Registro de cambios de textos y nombres de menús

**Base:** propuesta `DA06_Propuesta_Textos.xlsx` (en esta misma carpeta), revisada por el equipo: 18 filas acordadas.
**Rama:** `sgr/da06`, creada desde `main` (commit `0d63d04`).
**Verificación:** sistema local (`127.0.0.1:8010`), base `sgr_local` con datos ficticios, rol Administrador, 07-11-2026.
**Alcance:** solo textos visibles. No se cambiaron rutas, archivos, IDs, nombres de campos, permisos (`gobierno.ver`, `gobierno.configurar` y demás) ni lógica de datos.

## Resultado por fila

| Fila | Cambio | Archivos | Estado |
|---|---|---|---|
| 1 | Miga de Bandeja: "SGR / Seguimiento / Bandeja de validación" | `operacion.js` | Aplicado y verificado |
| 2 | Descripción de Bandeja: "Revisa los respaldos pendientes y registra tu decisión con observaciones." | `operacion.js` | Aplicado y verificado |
| 3 | Miga de Reportes: "SGR / Seguimiento / Reportes operativos", aunque cambie el tipo de registro | `operacion.js` | Aplicado y verificado |
| 4 | Descripción de Reportes con referencia a Metas ajustadas | `operacion.js` | Aplicado y verificado |
| 5 | Aviso de Ítems y metas; se conserva el enlace a Configuración de metas | `items-metas.html` | Aplicado y verificado |
| 6 | "Datos del sistema · Delegación activa" | `kpis.js` | Aplicado y verificado |
| 7 | "Gestión social" en miga y pestaña (también la miga del detalle del expediente) | `casos-sociales.js`, `casos-sociales.html` | Aplicado |
| 8 | Sección de la miga según el menú: Planilla, Tubo y Ficha del compromiso en "Gestión diaria"; Evidencias en "Seguimiento" | `operacion.js` | Aplicado y verificado |
| 9 | Miga de Alertas: "SGR / Seguimiento / Alertas operativas" | `alertas.js` | Aplicado |
| 10 | Miga de Reglas: "SGR / Administración / Reglas del flujo" | `gobierno.js` | Aplicado y verificado |
| 11 | Catálogos (Tipos de atención, Subatenciones, Clasificación): "Administración" para perfiles que mantienen; "Catálogos de consulta" para perfiles de solo consulta, igual que el grupo del menú | `tipos-atencion.html`, `subatenciones.html`, `clasificacion.js`, `layout.js` | Aplicado; verificado con Administrador. Caso de solo consulta verificado en código, pendiente de prueba con un perfil de consulta |
| 12 | Migas propias: "Ausencias y calendario" y "Metas ajustadas" | `ausencias.js` | Aplicado y verificado |
| 13 | Títulos de pestaña "<Pantalla> · SGR" en 9 páginas (Reglas: "Reglas del flujo · SGR") | 9 archivos `.html` | Aplicado; verificado en Tubo de trabajo |
| 14 | Pestañas "Vecinos · SGR" y "Juntas y organizaciones · SGR" | `vecinos.html`, `organizaciones.html` | Aplicado |
| 15 | Quitar asterisco del filtro "Configuración" en Clasificación | — | **No aplica:** en la versión actual ese filtro ya no existe; la pantalla solo tiene el buscador opcional, sin asterisco |
| 16 | Menú y título "Reglas del flujo"; se mantiene "Roles y permisos" | `layout.js`, `gobierno.js` | Aplicado y verificado |
| 17 | Se mantienen ambas entradas; cada vista con su propia descripción (Ausencias: disponibilidad; Metas ajustadas: cumplimiento) | `ausencias.js` | Aplicado y verificado |
| 18 | Textos heredados de Ítems adaptados en Períodos ("Nombre del período", etc.) y Configuración de metas ("Ítem", "Nueva meta", etc.), sin cambiar IDs ni nombres de campos | `periodos.html`, `configuraciones-metas.html` | Aplicado (marcado estático; la tabla y el formulario visibles los genera el JavaScript) |

## Evidencia

Carpeta `capturas/`: 8 capturas **antes** y 10 **después** (incluye el menú con "Reglas del flujo" y el título de pestaña "Tubo de trabajo · SGR").

## Notas para el revisor

- 25 archivos modificados, todos en `frontend/`; 44 reemplazos exactos, sin cambios de saltos de línea.
- Recargar sin caché (Ctrl + Shift + R): las páginas cargan los scripts con `?v=` fijo y el navegador puede mostrar la versión anterior.
- Para probar la fila 11 con perfil de consulta: crear un rol con `tipos-atencion.ver` sin `crear`/`editar`/`desactivar`; la miga debe decir "SGR / Catálogos de consulta / Tipos de atención".
