# Áreas operativas del Excel

Se reutiliza el mantenedor **Cargos y áreas**: el nombre identifica la entrada operativa numerada, el área agrupa su familia y la planilla selecciona el perfil de captura existente. El rol determina los permisos y se mantiene independiente.

## Procedencia del catálogo

Fuente: `Copia INACAP 3ER COMPAÑIAS MATRIZ SGR TRIMESTRE 2026 REV.xlsx`, hoja `SEMAFORO`, B4:B15 y enlaces de la columna M a las planillas.

| Entrada operativa | Celda | Planilla del sistema | Hoja enlazada |
| --- | --- | --- | --- |
| GESTOR SOCIAL 1 | B7 | G_SOC | G SOC 1 |
| GESTOR SOCIAL 2 | B5 | G_SOC | G SOC2 |
| GESTOR SOCIAL 3 | B4 | G_SOC | G SOC3 |
| GESTOR SOCIAL 4 | B10 | G_SOC | G SOC4 |
| GESTOR SOCIAL 5 | B6 | G_SOC | ` G SOC5` (espacio inicial) |
| TERRITORIAL OO.CC. 1 | B15 | T_OC | T OC1 |
| TERRITORIAL OO.CC. 2 | B9 | T_OC | T OC 2 |
| TERRITORIAL OO.CC. 3 | B14 | T_OC | T OC 3 |
| TERRITORIAL OO.CC. 4 | B12 | T_OC | T OC 4 |
| COOR SERV. COMU | B8 | COOR_DISERCO | COOR DISERCO |
| PLANIFICACIÓN Y GESTIÓN | B11 | PLAN_CON | PLAN y CON |
| APOYO ADMINISTRATIVO | B13 | AP_ADM | AP ADM. |

Los códigos `EXCEL-*` son identificadores internos generados por el sistema; no se presentan como códigos oficiales del Excel. Se conserva la etiqueta de SEMAFORO para planificación, aunque RESUMEN utiliza «PLANIFICACION Y CONTROL». La hoja GES SEG no pertenece a estas doce filas.

## Uso

1. Ingresar con permisos `cargos.ver` y `cargos.crear`.
2. Abrir Administración → Cargos y áreas → **Incorporar áreas del Excel**.
3. Revisar las doce filas y confirmar **Incorporar faltantes**. Cancelar no guarda nada.
4. En Administración → Usuarios, editar la cuenta y seleccionar su **Cargo / área operativa**. Guardar con los permisos habituales de Usuarios. No se infiere la asignación a partir de nombres de personas.

La operación conserva cargos anteriores y entradas compatibles, incluso inactivas; no reactiva ni sobrescribe registros. Si hay códigos, nombres o planillas incompatibles, aborta toda la incorporación. Cada alta registra versión de catálogo y auditoría con usuario, delegación y procedencia. Repetir no genera duplicados. No requiere migraciones de base de datos.

## Verificación local

- Nueve casos automatizados en `backend/core/test_area_catalog.py`: referencia sin escrituras, altas y conservación de datos previos, repetición, inactivos, conflictos de nombre o código, auditoría/versiones, permisos/confirmación y asignación a usuario con planilla sin modificar el rol.
- Recorrido en navegador con base SQLite separada: previsualización, cancelación sin cambios, incorporación de doce filas, repetición, vista móvil y opciones de selección en Usuarios; sin errores JavaScript.
- Regresión completa de `core` en MySQL: 365 casos, 364 aprobados y un fallo esperado preexistente; sin fallos inesperados. `manage.py check` sin incidencias.
- Las pruebas no asignan áreas a personas reales ni modifican los datos de AWS.

## Alcance pendiente

Esta etapa integra el catálogo y su asignación mediante el mantenedor existente. La asociación de ítems específicos a cada entrada requiere un mapeo confirmado; no se deduce automáticamente por familia. Los nombres de trabajadores del Excel no se importan. La unificación de atención, actividad y tubo corresponde a una etapa posterior. El despliegue y la incorporación del catálogo en AWS deben efectuarse expresamente; estas comprobaciones son locales.
