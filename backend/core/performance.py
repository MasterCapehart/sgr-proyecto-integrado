"""Avance validado/meta ajustada, ponderación y tope120. No altera registros."""
from decimal import Decimal
from django.db.models import Prefetch
from .models import Actividad,Evidencia,RevisionEvidencia
MAXIMUM=Decimal('120')
WARNING_FACTOR=Decimal('.60')
DETAIL_LIMIT=50

def reasons(activity,evidence):
    snapshot=activity.elegibilidad_snapshot
    result=[]
    if snapshot is None:result.append('Sin evaluación histórica capturada; no se presume candidatura.')
    elif snapshot.get('potencialmente_puntuable') is not True:
        result.extend(snapshot.get('motivos') or ['No cumple las reglas de candidatura capturadas.'])
    elif snapshot.get('clasificacion') in ['Coordinación','Otra gestión']:result.append('Clasificación excluida de cumplimiento.')
    if activity.estado!='Validada':result.append('La actividad no está validada: '+activity.estado+'.')
    current=[e for e in evidence if not hasattr(e,'siguiente_version') and e.estado!='Anulada']
    if not current:result.append('No tiene respaldos vigentes aprobados.')
    else:
        for e in current:
            revision=next(iter(e.revisiones.all()),None)
            if (e.estado!='Aprobada' or revision is None or revision.decision!='Aprobada' or revision.version_evidencia!=e.version
                or revision.autor_id in [activity.autor_id,e.autor_id]):
                result.append('Falta aprobación vigente del respaldo por un revisor distinto del autor.');break
    return result

def enrich(result,cal,period,user):
    from .absences import number
    evidence=Evidencia.objects.select_related('siguiente_version').prefetch_related(Prefetch('revisiones',queryset=RevisionEvidencia.objects.order_by('-pk')))
    activities=Actividad.objects.filter(autor=user,delegacion_id=cal.delegacion_id if cal else result['delegacion'],fecha__range=[period.fecha_inicio,period.fecha_fin],item_id__in=[m['item'] for m in result['metas']]).order_by('fecha','creado','pk').prefetch_related(Prefetch('evidencias',queryset=evidence))
    grouped={}
    for a in activities:grouped.setdefault(a.item_id,[]).append((a,reasons(a,list(a.evidencias.all()))))
    available=Decimal(result['dias_disponibles']) if result['dias_disponibles'] is not None else Decimal(0)
    elapsed=Decimal(result.get('dias_disponibles_transcurridos') or 0)
    goal=min(Decimal(1),elapsed/available)*100 if available>0 and elapsed>0 else None
    result.update(regla_cumplimiento=dict(version=1,tope_porcentaje='120',umbral_naranjo_relativo='60',orden='Fecha de realización, fecha de registro e identificador',aporte_por_actividad='1',limite_detalle=DETAIL_LIMIT),
        objetivo_al_dia=number(goal) if goal is not None else None,umbral_naranjo=number(goal*WARNING_FACTOR) if goal is not None else None)
    for row in result['metas']:
        records=grouped.get(row['item'],[]);target=Decimal(row['meta_ajustada_exacta']) if row['meta_ajustada_exacta'] is not None else None
        ceiling=target*MAXIMUM/100 if target is not None and target>0 and available>0 else None
        recognized=Decimal(0);valid=0;details=[];partial=0;above=0
        for activity,excluded in records:
            eligible=not excluded
            if eligible:valid+=1
            amount=min(Decimal(1),max(Decimal(0),ceiling-recognized)) if eligible and ceiling is not None else Decimal(0)
            recognized+=amount;note=list(excluded)
            if eligible:
                if ceiling is None:note.append('Sin meta o disponibilidad laboral evaluable; no se reconoce aporte.')
                elif amount==0:note.append('Sobre el tope del 120 %; se conserva la actividad completa.');above+=1
                elif amount<1:note.append('Cruce parcial del tope: solo se limita el aporte matemático, no la actividad.');partial+=1
                else:note.append('Actividad elegible con respaldos validados; aporta una unidad.')
            if len(details)<DETAIL_LIMIT:details.append(dict(id=activity.pk,codigo=activity.codigo,fecha=str(activity.fecha),estado=activity.estado,valida=eligible,reconocido=number(amount),reconocido_exacto=str(amount),motivos=note))
        percent=min(MAXIMUM,recognized/target*100) if ceiling is not None else None
        weight=Decimal(row['ponderacion'])
        weighted=percent*weight/100 if percent is not None and 0<=weight<=100 else None
        color='Sin calendario' if not cal else 'Sin jornada prevista' if target is None else 'Sin exigibilidad' if target==0 else 'Meta inválida' if target<0 else 'Sin jornada disponible' if available<=0 else 'Sin jornada transcurrida' if goal is None else 'Verde' if percent>=goal else 'Naranjo' if percent>=goal*WARNING_FACTOR else 'Rojo'
        row.update(total_registrado=len(records),validas=valid,excluidas=len(records)-valid,unidades_reconocidas=number(recognized),unidades_reconocidas_exactas=str(recognized),
            exceso_tope=number(Decimal(valid)-recognized) if ceiling is not None else None,limite_unidades=number(ceiling) if ceiling is not None else None,
            cumplimiento=number(percent) if percent is not None else None,cumplimiento_exacto=str(percent) if percent is not None else None,
            aporte_ponderado=number(weighted) if weighted is not None else None,semaforo=color,aportes=details,detalle_truncado=len(records)>DETAIL_LIMIT,registros_sobre_tope=above,registros_con_aporte_parcial=partial)
    result['alcance']='Cumplimiento de actividades elegibles con respaldos validados, limitado al 120 % por funcionario, ítem y período. No incluye felicitaciones ni otros componentes de evaluación; no calcula resultados colectivos.'
    return result

def lock_periods(activity_id):
    """Mismo orden que cierre: período→actividad→evidencia; sin reabrir cierres."""
    from .models import PeriodoGestion
    day=Actividad.objects.filter(pk=activity_id).values_list('fecha',flat=True).first()
    if day:list(PeriodoGestion.objects.select_for_update().filter(fecha_inicio__lte=day,fecha_fin__gte=day).order_by('pk'))
