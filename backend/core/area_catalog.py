"""Doce entradas operativas comprobadas en SEMAFORO B4:B15 del Excel.

Se reutiliza Cargo: nombre es la entrada operativa, area es su familia y
planilla es el perfil de captura existente. No se infieren personas ni permisos.
Los códigos EXCEL-* son identificadores internos, no códigos oficiales del libro.
"""
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from . import local_api as api, catalog_history
from .models import Cargo

SOURCE = 'Copia INACAP 3ER COMPAÑIAS MATRIZ SGR TRIMESTRE 2026 REV.xlsx'


def entry(code, name, family, profile, sheet, cell):
    return dict(codigo=code, nombre=name, area=family, planilla=profile,
                hoja=sheet, origen_excel='SEMAFORO!' + cell)


REFERENCE = (
    *(entry(f'EXCEL-GSOC-{i}', f'GESTOR SOCIAL {i}', 'GESTOR SOCIAL', 'G_SOC', sheet, cell)
      for i, sheet, cell in [(1, 'G SOC 1', 'B7'), (2, 'G SOC2', 'B5'), (3, 'G SOC3', 'B4'),
                             (4, 'G SOC4', 'B10'), (5, ' G SOC5', 'B6')]),
    *(entry(f'EXCEL-TOC-{i}', f'TERRITORIAL OO.CC. {i}', 'TERRITORIAL ORGANIZACIONES COMUNITARIAS', 'T_OC', sheet, cell)
      for i, sheet, cell in [(1, 'T OC1', 'B15'), (2, 'T OC 2', 'B9'), (3, 'T OC 3', 'B14'), (4, 'T OC 4', 'B12')]),
    entry('EXCEL-COOR', 'COOR SERV. COMU', 'COORDINADOR SERVICIOS COMUNITARIOS', 'COOR_DISERCO', 'COOR DISERCO', 'B8'),
    entry('EXCEL-PLAN', 'PLANIFICACIÓN Y GESTIÓN', 'PLANIFICACIÓN Y GESTIÓN', 'PLAN_CON', 'PLAN y CON', 'B11'),
    entry('EXCEL-ADM', 'APOYO ADMINISTRATIVO', 'APOYO ADMINISTRATIVO', 'AP_ADM', 'AP ADM.', 'B13'),
)


def preview(lock=False):
    rows = []
    for expected in REFERENCE:
        qs = Cargo.objects.filter(Q(codigo__iexact=expected['codigo']) | Q(nombre__iexact=expected['nombre']))
        if lock:
            qs = qs.select_for_update()
        found = list(qs.order_by('pk'))
        row = dict(expected, id=None, action='create', estado=True, detail='Se incorporará al catálogo.')
        if found:
            obj = found[0]
            if len(found) > 1 or obj.nombre.strip().casefold() != expected['nombre'].casefold() or obj.planilla != expected['planilla']:
                row.update(action='conflict', detail='Existe un código, nombre o planilla incompatible. Revisa el registro antes de incorporar.')
            else:
                row.update(id=obj.pk, action='keep', estado=obj.estado,
                           detail='Se conserva sin cambios.' if obj.estado else 'Se conserva inactivo; no se reactivará automáticamente.')
        rows.append(row)
    return dict(source=SOURCE, entries=rows,
                summary={key: sum(r['action'] == key for r in rows) for key in ('create', 'keep', 'conflict')},
                notes=['Los códigos EXCEL-* son internos del sistema.',
                       'Planificación conserva la etiqueta de SEMAFORO; RESUMEN utiliza PLANIFICACION Y CONTROL.',
                       'GES SEG no forma parte de estas doce filas y no se incorpora automáticamente.',
                       'No se asignan personas, roles, permisos ni ítems por esta operación.'])


@require_http_methods(['GET', 'POST'])
def reference(request):
    if not request.user.is_authenticated:
        return api.error('Inicia sesión.', 401)
    if not api.allowed(request.user, 'cargos', 'ver') or (request.method == 'POST' and not api.allowed(request.user, 'cargos', 'crear')):
        return api.error('No tienes permiso para administrar este catálogo.', 403)
    if request.method == 'GET':
        response = api.ok(preview())
        response['Cache-Control'] = 'private, no-store'
        return response
    if api.active_delegation(request) is None:
        return api.error('Selecciona una delegación autorizada.', 403)
    try:
        data = api.body(request)
        if set(data) != {'confirmar'} or data['confirmar'] is not True:
            return api.error('Confirma la incorporación de las áreas de referencia.')
        with transaction.atomic():
            plan = preview(lock=True)
            if plan['summary']['conflict']:
                return api.error('Hay coincidencias incompatibles. No se modificó ningún registro.', 409, plan)
            created = 0
            for row in plan['entries']:
                if row['action'] != 'create':
                    continue
                obj = Cargo(**{k: row[k] for k in ('codigo', 'nombre', 'area', 'planilla')})
                obj.full_clean()
                obj.save()
                catalog_history.record(request, 'cargos', obj)
                after = dict(catalog_history.catalog(obj), origen_excel=row['origen_excel'], archivo_origen=SOURCE)
                api.record_event(request, 'cargos', obj.pk, 'crear', None, after)
                created += 1
        return api.ok(dict(preview(), created=created))
    except (IntegrityError, ValidationError):
        return api.error('El catálogo cambió o tiene una coincidencia incompatible. Actualiza la vista; no se aplicaron cambios parciales.', 409)
