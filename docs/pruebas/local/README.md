# Pruebas locales

Fichas Word con las evidencias integradas, informe de pantallas y registros de ejecución local. Las versiones y fechas se interpretan según cada documento; los resultados antiguos no se convierten en pruebas nuevas al copiarlos.

## Documentos

| Prueba | Archivo |
|---|---|
| Login completo | [Ficha](documentos/Ficha_Prueba_Login_ACC01_Completa.docx) |
| Acceso mediante perfiles | [Ficha ACC01](documentos/Ficha_Prueba_ACC01_Roles_Completa.docx) |
| Seguridad del acceso y cierre de sesión | [Ficha ACC02–ACC03](documentos/Ficha_Prueba_ACC02_ACC03_Seguridad_Acceso.docx) |
| Recuperación por código | [Ficha ACC04–ACC06](documentos/Ficha_Prueba_ACC04_ACC05_ACC06_Recuperacion.docx) |
| Contexto y delegación autorizada | [Ficha ADM06](documentos/Ficha_Prueba_ADM06_Contexto_Delegacion.docx) |
| CRUD Delegaciones | [Ficha ADM01–ADM02](documentos/Ficha_Prueba_CRUD_Delegaciones_ADM01_ADM02.docx) |
| CRUD Roles | [Ficha ADM04](documentos/Ficha_Prueba_CRUD_Roles_ADM04.docx) |
| CRUD Usuarios | [Ficha ADM03](documentos/Ficha_Prueba_CRUD_Usuarios_ADM03.docx) |
| CRUD Ítems y metas | [Ficha CAT01](documentos/Ficha_Prueba_CRUD_ItemsMetas_CAT01.docx) |
| Tipos y subatenciones | [Ficha CAT02–CAT03](documentos/Ficha_Prueba_CRUD_Tipos_Subatenciones_CAT02_CAT03.docx) |
| Ingreso de atención ciudadana | [Ficha ACT05–ACT06](documentos/Ficha_Prueba_Ingreso_Atencion_ACT05_ACT06.docx) |
| Informe general de pantallas | [Informe Word](documentos/Informe_Pruebas_Pantallas_SGR.docx) |

La ficha básica `documentos/historico/Ficha_Prueba_Login_ACC01.docx` se conserva como versión anterior, sin imágenes. Para revisar el login usar la ficha completa; no sumar las dos como pruebas independientes.

## Archivos de evidencia

- [evidencias_fichas_corregidas/](evidencias_fichas_corregidas/): capturas y resultados vinculados con las fichas.
- [evidencias_pantallas_completas/](evidencias_pantallas_completas/): capturas de recorridos, resultados, listados Excel y registros publicados previamente sin configuración privada.
- [periodos-local/](periodos-local/README.md): calendario, cierre/reapertura y conciliación histórica. Su registro indica 344 pruebas ejecutadas, 343 aprobadas y una falla esperada heredada.
- [Regresión de integración](regresion/pruebas-servidor-traslado.txt): ejecución histórica de las pruebas del traslado local.
- [Código de pruebas del backend](../../../backend/core/): suites `test*.py`; no se duplican los módulos de aplicación en la documentación.

Las fichas incorporan sus propios estados y limitaciones. Conservarlas al preparar el cierre y la matriz; no afirmar que todas las variantes del plan se ejecutaron por disponer de una ficha.
