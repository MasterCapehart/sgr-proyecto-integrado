"""Revisión aritmética de pautas. No aprueba ni cambia ponderaciones."""
from decimal import Decimal,InvalidOperation
from types import SimpleNamespace
from django.views.decorators.http import require_http_methods
from . import local_api as api
from .absences import meta_rows,number
from .models import Cargo,PeriodoGestion


def row(cargo,name,metas):
    weights=[Decimal(str(m['ponderacion'])) for m in metas]
    total=sum(weights,Decimal(0));missing=max(Decimal(0),100-total);excess=max(Decimal(0),total-100)
    invalid=any(not 0<w<=100 for w in weights)
    state='Sin metas' if not metas else 'Valores inválidos' if invalid else 'Incompleta' if total<100 else 'Excede 100 %' if total>100 else 'Suma 100 %'
    return dict(cargo=cargo,cargo_nombre=name,metas=len(metas),suma=number(total),faltante=number(missing),exceso=number(excess),estado=state,aprobada=False,
                configuraciones=[m['id'] for m in metas])


@require_http_methods(['GET'])
def overview(request):
    if not request.user.is_authenticated:return api.error('Inicia sesión.',401)
    if not api.allowed(request.user,'configuraciones-metas','ver'):return api.error('Sin permiso de consulta de metas.',403)
    if set(request.GET)-{'periodo'}:return api.error('Filtros no permitidos.')
    value=request.GET.get('periodo','')
    if not value.isascii() or not value.isdigit():return api.error('Selecciona un período válido.')
    period=PeriodoGestion.objects.filter(pk=value).first()
    if not period:return api.error('Período no encontrado.')
    rows=[]
    if period.cerrado:
        saved=period.parametros_cierre.get('metas')
        source='Parámetros del cierre' if isinstance(saved,list) else 'Cierre sin parámetros de metas'
        if not isinstance(saved,list):saved=[]
        if any(not isinstance(m,dict) for m in saved):return api.error('El cierre no conserva parámetros de ponderación interpretables.')
        # El cierre antiguo no guarda asociaciones históricas ítem/cargo.
        # Mostrar cada alcance conservado sin reconstruir respaldos generales.
        grouped={}
        for meta in saved or []:
            if not meta.get('estado'):continue
            cargo=meta.get('cargo');name=meta.get('cargo_nombre') or ('Cargo histórico sin etiqueta' if cargo else 'General')
            grouped.setdefault((cargo,name),[]).append(meta)
        try:rows=[row(c,n,ms) for (c,n),ms in grouped.items()]
        except (InvalidOperation,KeyError,TypeError):return api.error('El cierre no conserva parámetros de ponderación interpretables.')
        note='Se suman los alcances guardados al cierre, sin reconstruir asociaciones históricas ni aplicar hoy las metas generales a cargos pasados.'
    else:
        source='Configuraciones vigentes'
        scopes=[(None,'General')]+list(Cargo.objects.filter(estado=True).values_list('pk','nombre').order_by('nombre'))
        for cargo,name in scopes:
            metas=list(meta_rows(SimpleNamespace(cargo_id=cargo,is_superuser=False),period).values('pk','ponderacion'))
            rows.append(row(cargo,name,[dict(id=m['pk'],ponderacion=m['ponderacion']) for m in metas]))
        note='Por cargo se utiliza la meta específica activa de cada ítem; si falta, la general aplicable, sin sumarlas dos veces. Solo ítems activos disponibles para el cargo.'
    response=api.ok(dict(periodo=period.pk,periodo_nombre=period.nombre,cerrado=period.cerrado,fuente=source,pautas=rows,criterio=note,
        advertencia='Sumar 100 % no acredita que estén todos los componentes ni que la pauta esté aprobada. No se completan pesos ni se normaliza una pauta incompleta. Las excepciones formales siguen pendientes de definición.'))
    response['Cache-Control']='private, no-store'
    return response
