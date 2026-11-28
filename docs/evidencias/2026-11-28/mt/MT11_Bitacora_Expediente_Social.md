# MT11 - Bitácora de Pruebas: Expediente Social y Tiempos de Gestión
**Responsable:** Matías | **Fecha:** 28/11/2026 | **Etapa:** 14. Pruebas funcionales | **Estado:** Terminada

## 1. Propósito
Acreditar la ejecución del Caso Integral E07: Expediente social con 3 gestiones reales y cálculo exacto de tiempos vs caso incompleto.

## 2. Resultados de Ejecución

| Escenario | Parámetros de Prueba | Resultado Esperado | Resultado Obtenido | Estado |
|---|---|---|---|:---:|
| **Expediente Completo** | Ingreso 05/01, Entrevista 07/01, Visita 12/01, Informe 16/01 | T1=2d, T2=5d, T3=4d, T4=11d | Cálculos exactos sin desfase | [x] Aprobado |
| **Visita Futura / Incompleta** | Visita programada con fecha futura | No debe calcular tiempo negativo | Sistema muestra `No calculable` | [x] Aprobado |
| **Fechas Ausentes** | Expediente sin registro de informe social | T3 reportado como no calculable | Valor informativo sin error 500 | [x] Aprobado |
