"""Consolidación de resultados individuales; nunca compensa aportes sobre el tope."""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from . import absence_api as access, absences, local_api as api
from .models import Actividad

D=Decimal

def metric(rows):
    """Normaliza pesos de ítems compatibles; no mezcla unidades entre ítems."""
    usable=[r for r in rows if r.get('cumplimiento_exacto') is not None]
    if not usable or any(r.get('peso') is None for r in usable):return None,None
    weights=sum((D(r['peso']) for r in usable),D(0))
    if weights<=0:return None,None
    value=sum((D(r['cumplimiento_exacto'])*D(r['peso']) for r in usable),D(0))/weights
    objectives=[r for r in usable if r.get('objetivo_exacto') is not None]
    goal=sum((D(r['objetivo_exacto'])*D(r['peso']) for r in objectives),D(0))/weights if len(objectives)==len(usable) else None
    return value,goal

def status(value,goal):
    if value is None or goal is None:return 'Sin evaluación'
    return 'Verde' if value>=goal else 'Naranjo' if value>=goal*D('.6') else 'Rojo'

def consolidate(summaries):
    grouped={};persons=[]
    for summary in summaries:
        individual=[]
        for row in summary.get('metas',[]):
            valid=row.get('cumplimiento_exacto') is not None and row.get('meta_ajustada_exacta') is not None
            group=grouped.setdefault(row.get('item',row['id']),dict(id=row.get('item',row['id']),codigo=row.get('codigo',''),nombre=row.get('nombre','Ítem histórico'),unidad=row.get('unidad',''),meta=D(0),reconocido=D(0),validas=0,registradas=0,exceso=D(0),evaluados=0,sin_evaluacion=0,pesos=set(),objetivo_numerador=D(0),objetivos_completos=True))
            if not valid:group['sin_evaluacion']+=1;continue
            target=D(row['meta_ajustada_exacta']);recognized=D(row['unidades_reconocidas_exactas']);weight=D(row['ponderacion'])
            group['meta']+=target;group['reconocido']+=recognized;group['validas']+=row['validas'];group['registradas']+=row['total_registrado'];group['exceso']+=D(row['validas'])-recognized;group['evaluados']+=1;group['pesos'].add(weight)
            objective=summary.get('objetivo_al_dia')
            if objective is None:group['objetivos_completos']=False
            else:group['objetivo_numerador']+=target*D(objective)
            individual.append(dict(cumplimiento_exacto=row['cumplimiento_exacto'],peso=str(weight) if 0<=weight<=100 else None,objetivo_exacto=objective))
        value,goal=metric(individual)
        persons.append(dict(id=summary['funcionario'],nombre=summary['funcionario_nombre'],area=summary.get('area',''),cumplimiento=absences.number(value) if value is not None else None,semaforo=status(value,goal),items_evaluados=len(individual),items_sin_evaluacion=len(summary.get('metas',[]))-len(individual)))
    items=[]
    for g in grouped.values():
        value=g['reconocido']/g['meta']*100 if g['meta']>0 else None
        goal=g['objetivo_numerador']/g['meta'] if g['meta']>0 and g['objetivos_completos'] else None
        weights=g.pop('pesos');weight=next(iter(weights)) if len(weights)==1 else None
        if weight is not None and not 0<=weight<=100:weight=None
        g.pop('objetivo_numerador');g.pop('objetivos_completos')
        for k in ['meta','reconocido','exceso']:g[k]=absences.number(g[k]) if g['evaluados'] else None
        g.update(cumplimiento=absences.number(value) if value is not None else None,cumplimiento_exacto=str(value) if value is not None else None,peso=str(weight) if weight is not None else None,objetivo_exacto=str(goal) if goal is not None else None,semaforo=status(value,goal))
        items.append(g)
    items.sort(key=lambda r:r['codigo']);persons.sort(key=lambda r:r['nombre'].casefold())
    value,goal=metric(items)
    return dict(items=items,personas=persons,cumplimiento=absences.number(value) if value is not None else None,semaforo=status(value,goal),evaluados=sum(p['cumplimiento'] is not None for p in persons),sin_evaluacion=sum(p['cumplimiento'] is None for p in persons),distribucion={color:sum(p['semaforo']==color for p in persons) for color in ['Verde','Naranjo','Rojo','Sin evaluación']},parcial=any(p['items_sin_evaluacion'] or not p['items_evaluados'] for p in persons),pesos_compatibles=all(i['peso'] is not None for i in items if i['cumplimiento'] is not None))

@require_http_methods(['GET'])
def overview(request):
    denied=access.gate(request)
    if denied:return denied
    if not access.manager(request.user) or not api.allowed(request.user,'ausencias','ver_equipo'):return api.error('Solo administrador y delegado con permiso de equipo pueden consultar el tablero colectivo.',403)
    try:
        if set(request.GET)-{'periodo','area'}:raise ValidationError('Filtros no permitidos. Se utiliza únicamente la delegación activa autorizada.')
        period=access.period(request.GET.get('periodo'));delegation=api.active_delegation(request);area=request.GET.get('area','').strip()
        if len(area)>100:raise ValidationError('Área inválida.')
        people=access.people(request).select_related('cargo')
        areas=sorted({u.cargo.area for u in people if u.cargo_id and u.cargo.area}) if not period.cerrado else []
        if period.cerrado:
            if area:raise ValidationError('El cierre no conserva áreas históricas. Consulta el consolidado completo de la delegación.')
            summaries=[s for s in period.parametros_cierre.get('ajustes_ausencia',[]) if s['delegacion']==delegation.pk]
            territories=[]
        else:
            if area:people=people.filter(cargo__area=area)
            people=list(people);summaries=[dict(absences.summary(delegation,u,period),area=u.cargo.area if u.cargo_id else '') for u in people]
            territories_by_key={}
            for row in Actividad.objects.filter(delegacion=delegation,autor__in=people,fecha__range=[period.fecha_inicio,period.fecha_fin]).values('sector').annotate(total=Count('pk')):
                label=' '.join((row['sector'] or '').split()) or 'Sin territorio';key=label.casefold()
                entry=territories_by_key.setdefault(key,dict(nombre=label,registradas=0));entry['registradas']+=row['total']
            territories=sorted(territories_by_key.values(),key=lambda r:(-r['registradas'],r['nombre'].casefold()))
        data=consolidate(summaries)
        data.update(delegacion=delegation.nombre,periodo=period.nombre,cerrado=period.cerrado,areas=areas,area=area,territorios=territories,fuente='Resultados conservados al cierre; sin reconstruir equipo ni territorios históricos.' if period.cerrado else 'Equipo activo autorizado y calendarios vigentes.',regla='Por ítem: suma del aporte limitado de cada persona / suma de sus metas ajustadas exactas. Índice consolidado: media de cumplimientos por ítem ponderada por sus pesos compatibles, normalizados. No es el puntaje integral del sistema.',territorios_nota='Distribución operativa de registros, sin porcentaje de cumplimiento: no existen metas territoriales asignadas. En períodos cerrados no se reconstruyen territorios con datos actuales.')
        return api.ok(data)
    except (ValidationError,ValueError,TypeError) as ex:return access.failure(ex)
