"""Recalcula métricas desde la traza conservada; no llama a AWS ni ejecuta carga."""
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / '.archivo/interno/2026-10-17/evidencias/rendimiento-aws'

def main():
    trace = SOURCE / 'solicitudes.jsonl'
    samples = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
    grouped = defaultdict(list)
    for sample in samples:
        grouped[(sample['stage'], sample['operation'])].append(sample)
    fields = ['etapa', 'operacion', 'solicitudes', 'fallos', 'promedio_ms', 'p95_ms', 'p99_ms', 'max_ms', 'sobre_2s', 'sobre_5s']
    rows = []
    for (stage, operation), values in sorted(grouped.items()):
        latencies = sorted(float(v['ms']) for v in values)
        percentile = lambda p: latencies[max(0, math.ceil(len(latencies) * p) - 1)]
        rows.append(dict(zip(fields, [stage, operation, len(values), sum(not v['ok'] for v in values),
            round(statistics.mean(latencies), 2), percentile(.95), percentile(.99), max(latencies),
            sum(v > 2000 for v in latencies), sum(v > 5000 for v in latencies)])))
    with (HERE / 'metricas_recalculadas.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with (SOURCE / 'metricas.csv').open() as stream:
        reported = {(r['etapa'], r['operacion']): r for r in csv.DictReader(stream)}
    differences = []
    for row in rows:
        key = (row['etapa'], row['operacion'])
        for field in fields[2:]:
            if key not in reported or abs(float(row[field]) - float(reported[key][field])) > .011:
                differences.append({'stage': key[0], 'operation': key[1], 'field': field})
    if set(reported) != set(grouped):
        differences.append({'field': 'group_coverage'})
    summary = {'source_sha256': hashlib.sha256(trace.read_bytes()).hexdigest(), 'requests': len(samples),
        'failed_requests': sum(not s['ok'] for s in samples), 'groups': len(rows),
        'percentile_method': 'nearest rank: sorted[ceil(n*p)-1]',
        'includes_client_timeouts': True, 'matches_published_metrics': not differences,
        'differences': differences, 'scope': 'Métricas de rendimiento del laboratorio; no cálculos del motor de metas o semáforos; no nueva ejecución AWS.'}
    (HERE / 'verificacion_calculos.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary, ensure_ascii=False))
    if differences:
        raise SystemExit('Métricas diferentes: revisar antes de aprobar la documentación.')

if __name__ == '__main__':
    main()
