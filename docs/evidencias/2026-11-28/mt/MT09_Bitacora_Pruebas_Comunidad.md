# MT09 - Bitácora de Pruebas: Vecinos, Juntas y Participación Comunitaria
**Responsable:** Matías | **Fecha:** 28/11/2026 | **Etapa:** 14. Pruebas funcionales | **Estado:** Terminada

## 1. Propósito
Acreditar la ejecución del Caso Integral E06: Creación de vecino -> Asociación a organización -> Cargo de dirigente -> Desactivación con conservación de historial.

## 2. Resultados de Ejecución

| Paso | Acción Realizada | Resultado Esperado | Resultado Obtenido | Estado |
|:---:|---|---|---|:---:|
| 1 | Crear vecino con RUN válido `11.234.567-1` (Carlos Mondaca) | Registro exitoso en delegación | Creado con código interno y versión 1 | [x] Aprobado |
| 2 | Intentar crear vecino con RUN con dígito verificador erróneo `11.234.567-8` | Rechazo con mensaje de validación | Error 400: El dígito verificador del RUN no es válido | [x] Aprobado |
| 3 | Registrar JJVV San Joaquín Alto en territorio asignado | Organización guardada | Registro creado en catálogo | [x] Aprobado |
| 4 | Asignar al vecino como Presidente de la JJVV | Cargo vigente registrado | Cargo asociado con fecha inicio | [x] Aprobado |
| 5 | Desactivar dirigente registrando fecha de término y motivo | Historial conservado sin borrado físico | Estado inactivo, historial consultable | [x] Aprobado |
