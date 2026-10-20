"""Aprovisionamiento trazable de ítems de captura, sin importar personas ni metas."""
import json
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Cargo, ItemMeta
from . import catalog_history, local_api as api

CATALOG = json.loads(Path(__file__).with_name('data').joinpath('area_items.json').read_text())


def normalize(text):
    return ' '.join(text.split()).casefold()


def configure(request, apply=False):
    if not request.user.is_active or not request.user.is_superuser:
        raise ValidationError('El aprovisionamiento requiere un administrador del sistema.')
    with transaction.atomic():
        cargos = list(Cargo.objects.select_for_update().all())
        existing = list(ItemMeta.objects.select_for_update().all())
        plan = []
        for entry in CATALOG['items']:
            selected = []
            for origin in entry['origenes']:
                matches = [c for c in cargos if normalize(c.nombre) == normalize(origin['area'])]
                if len(matches) != 1 or not matches[0].estado:
                    raise ValidationError('Área ausente, duplicada o inactiva: ' + origin['area'])
                selected.append(matches[0].pk)
            matches = [i for i in existing if normalize(i.nombre) == normalize(entry['nombre'])]
            if len(matches) > 1:
                raise ValidationError('Nombre de ítem ambiguo: ' + entry['nombre'])
            obj = matches[0] if matches else None
            if obj and (not obj.estado or normalize(obj.unidad_medida) not in {normalize(entry['unidad_medida']), '1'}):
                raise ValidationError('Ítem inactivo o unidad incompatible: ' + entry['nombre'])
            if not obj and any(i.codigo == entry['codigo'] for i in existing):
                raise ValidationError('Código ocupado: ' + entry['codigo'])
            plan.append((entry, obj, set(selected)))
        created = linked = 0
        for entry, obj, selected in plan:
            if not apply:
                continue
            before = catalog_history.catalog(obj) if obj else None
            missing = selected - set(obj.cargos.values_list('pk', flat=True)) if obj else selected
            if obj and not missing:
                continue
            if obj is None:
                obj = ItemMeta(**{k: entry[k] for k in ('codigo', 'nombre', 'unidad_medida')})
                obj.full_clean(); obj.save(); created += 1
            else:
                catalog_history.freeze_references('items-metas', obj)
                catalog_history.record(request, 'items-metas', obj, observed=True)
                obj.version += 1; obj.save(update_fields=['version'])
            obj.cargos.add(*missing); linked += len(missing)
            catalog_history.record(request, 'items-metas', obj)
            after = dict(catalog_history.catalog(obj), origenes=entry['origenes'], archivo_origen=CATALOG['fuente'])
            api.record_event(request, 'items-metas', obj.pk, 'crear' if before is None else 'editar', before, after)
        return {'items': len(plan), 'relations': sum(len(ids) for _, _, ids in plan),
                'created': created, 'linked': linked, 'applied': apply}
