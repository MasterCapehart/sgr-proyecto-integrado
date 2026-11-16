"""Completa metadatos ausentes únicamente para trimestres calendario inequívocos."""
import calendar
from datetime import date
from django.db import migrations


def complete_quarters(apps, schema_editor):
    Period = apps.get_model('core', 'PeriodoGestion')
    periods = Period.objects.using(schema_editor.connection.alias)
    for period in periods.filter(cerrado=False).iterator():
        start, end = period.fecha_inicio, period.fecha_fin
        if not start or not end or start.day != 1 or start.month not in (1, 4, 7, 10):
            continue
        year, quarter = start.year, (start.month - 1) // 3 + 1
        month = quarter * 3
        if end != date(year, month, calendar.monthrange(year, month)[1]):
            continue
        # Nunca sobrescribir una configuración explícita contradictoria.
        if period.anio not in (None, year) or period.numero not in (None, quarter):
            continue
        changes = {}
        if period.anio is None:
            changes['anio'] = year
        if period.numero is None:
            changes['numero'] = quarter
        if changes:
            periods.filter(pk=period.pk).update(**changes)


class Migration(migrations.Migration):
    dependencies = [('core', '0036_carta_numero_original_opcional')]
    operations = [migrations.RunPython(complete_quarters, migrations.RunPython.noop)]
