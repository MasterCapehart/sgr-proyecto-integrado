"""Prorrateo por medias jornadas únicas. No calcula rendimiento ni puntaje."""
from datetime import date,timedelta
from decimal import Decimal,ROUND_HALF_UP
from .models import CalendarioFuncionario,ConfiguracionMeta
from .excel_support import items_for
SLOTS={'No laboral':set(),'Completa':{0,1},'Mañana':{0},'Tarde':{1}}
def number(n):return str(Decimal(n).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def parse(v):return date.fromisoformat(str(v))
def meta_rows(user,period):
    return ConfiguracionMeta.objects.filter(periodo_gestion=period,estado=True,conciliada_con__isnull=True,item__in=items_for(user)).select_related('item').order_by('item__codigo')
def calculate(cal,period,user):
    metas=meta_rows(user,period);planned=set();away=set();rows=[]
    if cal:
        day=parse(period.fecha_inicio);end=parse(period.fecha_fin);off=set(cal.no_laborables)
        while day<=end:
            if str(day) not in off:planned.update((str(day),slot) for slot in SLOTS[cal.semana[day.weekday()]])
            day+=timedelta(days=1)
        for a in cal.ausencias.filter(estado='Autorizada'):
            day=max(parse(a.inicio),parse(period.fecha_inicio));end=min(parse(a.fin),parse(period.fecha_fin))
            while day<=end:
                away.update((str(day),slot) for slot in SLOTS[a.jornada]);day+=timedelta(days=1)
        away &= planned
    p=Decimal(len(planned))/2;a=Decimal(len(away))/2;available=p-a;ratio=available/p if p else None
    for m in metas:
        proportional=bool(cal and m.pk in cal.metas_prorrateables)
        adjusted=None if not cal or (proportional and ratio is None) else m.meta_esperada*ratio if proportional else m.meta_esperada
        state='Sin calendario' if not cal else 'Sin jornada prevista' if proportional and ratio is None else 'Sin exigibilidad por ausencia' if proportional and available==0 else 'Meta ajustada' if proportional else 'Meta sin prorrateo'
        rows.append(dict(id=m.pk,item=m.item_id,codigo=m.item.codigo,nombre=m.item.nombre,unidad=m.item.unidad_medida,meta_original=number(m.meta_esperada),meta_ajustada=number(adjusted) if adjusted is not None else None,
            meta_ajustada_exacta=str(adjusted) if adjusted is not None else None,prorrateable=proportional,version_meta=m.version,estado=state,cumplimiento=None,semaforo='Sin evaluación de desempeño'))
    state='Sin calendario' if not cal else 'Sin jornada prevista' if not p else 'Sin exigibilidad por ausencia' if not available else 'Disponibilidad calculada'
    return dict(delegacion=cal.delegacion_id if cal else None,funcionario=user.pk,funcionario_nombre=user.get_full_name() or user.username,periodo=period.pk,periodo_nombre=period.nombre,
        estado=state,calendario=cal.pk if cal else None,version_calendario=cal.version if cal else None,dias_previstos=number(p) if cal else None,dias_ausencia=number(a) if cal else None,dias_disponibles=number(available) if cal else None,
        factor=str(ratio) if ratio is not None else None,porcentaje_disponibilidad=number(ratio*100) if ratio is not None else None,metas=rows,periodo_cerrado=period.cerrado,
        alcance='Meta esperada ajustada por disponibilidad. No otorga puntos ni calcula el porcentaje de desempeño; semáforo pendiente del motor de evaluación.')
def closure(period):
    return [calculate(c,period,c.funcionario) for c in period.calendarios_funcionarios.select_related('funcionario').order_by('pk')]
def summary(delegation,user,period):
    if period.cerrado:
        saved=next((x for x in period.parametros_cierre.get('ajustes_ausencia',[]) if x['delegacion']==delegation.pk and x['funcionario']==user.pk),None)
        if saved:return dict(saved,periodo_cerrado=True,fuente='Parámetros del cierre')
        result=calculate(None,period,user);result['metas']=[]
        result['alcance']='El cierre no conserva un calendario de este funcionario. No se reconstruyen metas históricas usando su cargo o catálogo actual.'
        return dict(result,fuente='Cierre sin calendario de disponibilidad')
    cal=CalendarioFuncionario.objects.filter(delegacion=delegation,funcionario=user,periodo=period).first()
    return dict(calculate(cal,period,user),fuente='Calendario vigente')
