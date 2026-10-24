# Contraste de fórmulas entregadas y cálculo implementado

Fecha: 23/10/2026. Trabajo local de revisión y pruebas. Sin cambios al motor, interfaz, Excel o datos de AWS.

## Fuentes y precedencia

- `Guia_Proyecto_Software_SGR_Alumnos.pdf`: reglas RN-001 a RN-011, páginas 11–12; línea base académica §13.1, página 27.
- `Requisitos_y_Plan_Pruebas_Segunda_Evaluacion_SGR.pdf`: B3, página 7, lotes CAL-A a CAL-F.
- `PRESENTACIÓN MATRIZ REGIMIENTO RESULTADO.pptx`: diapositivas 9, 12, 14 y 16–19.
- Matriz Excel del tercer trimestre de 2026: hojas personales, SALON, TUBO, SEMAFORO, RESUMEN y RECLAMOS.
- Nuevos requerimientos y decisiones posteriores del usuario: el tope de 120 % reemplaza el 150 % original; plazo de tres fechas inclusivas, elegibilidad, cupo diario y ajuste de metas por ausencias.

Los documentos académicos explicitan fórmulas; no todo está pendiente. No obstante, una celda del Excel no valida automáticamente una regla: hay porcentajes literales, referencias inconsistentes, pautas incompletas y fórmulas de emergencias con meta igual al avance.

## Matriz de contraste

| Fuente | Esperado entregado | Resultado contrastado | Estado |
|---|---|---|---|
| CAL-A | I01: 8/10=80 %, peso40 →32 puntos. I02:10/20=50 %, peso60 →30. Total62 | Resumen real de metas devuelve32 y30; suma62. Índice de persona del colectivo coincide en62 cuando pesos suman100 | Coincide para pauta completa del ensayo |
| CAL-B | Tope antiguo150: avance20/meta10, peso40 →60; más30 →90 | Regla nueva120: reconoce12 de20, cumplimiento120 %, aporte48; más30 →78 | Diferencia correcta por R10 posterior; no volver a150 |
| CAL-C | 10 compromisos:8 realizados,1 pendiente,1 en proceso →80 %/20 % | KPI real entrega total10, realizados8 y en curso2. No entrega porcentaje del tubo ni aporte ponderado | Conteos correctos; porcentaje y aporte de puntaje pendientes |
| CAL-D | Calendario de ensayo de30 días inclusivos; día15 →50 %, antes0 y después100 | Configurado explícitamente con7 días laborables, calcula30 días,50 % al15 y100 % después; antes devuelve objetivo sin evaluación (null) | Coincide dentro/después; diferencia explícita antes del inicio: neutral |
| CAL-E | Esperado50:29,99 rojo;30 y49,99 ámbar;50 verde | Función de color del colectivo devuelve los cuatro colores esperados;29,999 sigue rojo antes de redondear | Coincide en la función de color probada |
| CAL-F | Umbral colectivo80:79,99 no alcanza,80 alcanza; tubo80 %/meta80 %=100 % del ítem | No hay servicio de evaluación por umbral80 configurable ni ítem porcentual del tubo integrado en el motor cuantitativo | Pendiente; no se marca como prueba aprobada |
| Pauta parcial | No confundir aporte sobre pauta con índice normalizado | Un ítem con10 % de cumplimiento y peso20 da2 puntos de aporte; índice parcial normalizado del tablero da10 % | Diferencia real documentada; no es puntaje integral |

Las seis pruebas automatizadas validan CAL-A, CAL-B actualizado, conteos CAL-C, CAL-D con calendario explícito, función de color CAL-E y diferencia entre índice parcial y aporte. No certifican el puntaje completo, CAL-F ni una aprobación institucional de la pauta.

## Fórmulas base conservadas

- Avance: actividades válidas del ítem en el período; varias evidencias no duplican una actividad.
- Cumplimiento por ítem: avance reconocido / meta ajustada ×100, con tope120 %.
- Aporte: cumplimiento × peso en puntos porcentuales /100.
- Total de pauta completa: suma de aportes ponderados, manteniendo pesos aprobados por cargo/período. No normalizar silenciosamente una pauta incompleta.
- Ajuste proporcional: meta base × días disponibles / días previstos, únicamente para metas seleccionadas como prorrateables.
- Esperado diario: días disponibles transcurridos / días disponibles del período ×100. En ausencia de disponibilidad evaluable, estado neutral.
- Color: verde desde lo esperado, ámbar desde0,60 de lo esperado y rojo por debajo.

## Pendientes ordenados para completar la medición

1. **Pauta completa y vigencia:** validar suma100 % por cargo/período o excepción formal; distinguir borrador/pendiente de una pauta aprobada. Las49 metas fijas ya cargadas no contienen todos los componentes del puntaje.
2. **Parámetros versionados:** hacer configurables y visibles los umbrales/tope según vigencia; conservar120 como valor vigente, sin restaurar150. Actualmente tope120 y factorámbar0,60 son constantes.
3. **Tubo porcentual:** denominador de compromisos distintos, tratamiento sin compromisos y período/responsable; después fórmula del ítem porcentual y peso aprobado. El80 % de cumplimiento del tubo no es el umbral diario del semáforo.
4. **Emergencias:** resolver meta dinámica independiente; no convertir avance/avance en una meta fija ni fijar cero o uno por suposición.
5. **Puntaje integral:** sumar componentes con pauta aprobada; separar del índice parcial actual.
6. **Ajustes especiales:** importe, peso y vigencia aprobados de felicitaciones y penalizaciones, además de su elegibilidad y respaldo ya definidos.
7. **Territorios:** metas y agregación explícitas antes de publicar un porcentaje territorial.

Los tres asuntos aplazados por el usuario (puntaje integral, puntos de felicitaciones y metas territoriales) permanecen aplazados: esta revisión no los implementa.

## Evidencia y reproducción

Archivo de pruebas: `backend/core/test_calculos_fuentes.py`.

```text
DB_NAME=sgr_unified_qa backend/venv/bin/python backend/manage.py test core.test_calculos_fuentes --noinput
```

Resultado: **6 pruebas correctas**, en base temporal con datos ficticios. [Salida local](pruebas-locales.txt).

Estas pruebas usan registros/evidencias de fixture para contrastar fórmulas existentes; no prueban el flujo completo de ingreso, cupos y revisión por interfaz. Esos controles tienen sus pruebas independientes.

Comprobación conjunta con cumplimiento y colectivos: **29 pruebas correctas**. [Salida conjunta](pruebas-relacionadas.txt). No se modificaron los servicios de cálculo.
