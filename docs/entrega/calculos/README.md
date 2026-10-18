# Revisión independiente de las métricas de rendimiento

Se recalcularon los resultados desde la traza JSONL histórica, sin utilizar el resumen original como entrada del cálculo y sin hacer peticiones a la aplicación. Después se compararon con el CSV publicado.

- Solicitudes: 342; fallidas: 11; grupos etapa/operación: 18.
- Promedio: suma de latencias dividida por cantidad de solicitudes del grupo.
- p95 y p99: rango más cercano, posición `ceil(n × p)`, con las latencias ordenadas de menor a mayor.
- Máximo: mayor latencia observada. Se incluyen tiempos de espera de solicitudes fallidas; no se confunden con una respuesta HTTP completada.
- Excedencias: número de solicitudes con tiempo estrictamente mayor a 2.000 y 5.000 ms.
- Comparación: conteos y valores por cada grupo. Tolerancia 0,011 ms por redondeo del promedio a dos decimales; el archivo JSON identifica la huella SHA-256 de la traza.

Reproducir desde la raíz del repositorio, con Python 3:

```bash
python3 docs/entrega/calculos/recalcular_metricas.py
```

El script usa solo la biblioteca estándar. Genera `metricas_recalculadas.csv` y `verificacion_calculos.json` en esta carpeta y falla si detecta diferencias con el CSV histórico. No modifica la traza ni sus resultados originales.

**Alcance:** es una revisión independiente de métricas de rendimiento. No acredita fórmulas de metas, ponderaciones, cumplimiento, cálculo diario ni semáforos. Esos cálculos funcionales permanecen pendientes según el alcance documentado.
