"""Tres fechas calendario inclusivas; siete candidatas por autor/realización."""
from copy import deepcopy
from datetime import date,timedelta
from zoneinfo import ZoneInfo
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from .models import Actividad,ControlCupoFuncionario

TZ=ZoneInfo('America/Santiago')
MAXIMUM=7
LATE='Registrada fuera de plazo: no aporta a puntos ni metas.'
COMPLETED_LATE='Requisitos completados o recuperados fuera del plazo de tres días: no aporta a puntos ni metas.'
FULL='Cupo diario completo: máximo 7 actividades potencialmente puntuables por funcionario y fecha de realización. La actividad no se guardó; revisa las candidaturas de ese día.'

def ensure_author(identifier):
    # Commit first creation before business locks; duplicate inserts otherwise deadlock
    # when concurrent transactions upgrade their unique-key locks.
    ControlCupoFuncionario.objects.get_or_create(usuario_id=identifier)

def lock_author(identifier):
    # A dedicated row avoids locking the account referenced by unrelated audit inserts.
    ControlCupoFuncionario.objects.select_for_update().get(usuario_id=identifier)

def previous(obj):
    return dict(fecha=str(obj.fecha),eligibilidad=deepcopy(obj.elegibilidad_snapshot),reservado=obj.cupo_diario_reservado,creado=obj.creado)

def used(author,day,exclude=None):
    legacy=Q(elegibilidad_snapshot__control_registro__isnull=True,elegibilidad_snapshot__potencialmente_puntuable=True)
    qs=Actividad.objects.filter(autor_id=author,fecha=day).filter(Q(cupo_diario_reservado=True)|legacy)
    if exclude:qs=qs.exclude(pk=exclude)
    return qs.count()

def apply(obj,result,prior=None,preview=False):
    day=date.fromisoformat(str(obj.fecha));now=timezone.localtime(timezone.now(),TZ);today=now.date()
    if prior and prior['fecha']!=str(day):raise ValidationError('La fecha de realización queda fija después de guardar. Las correcciones no permiten cambiarla para recuperar plazo o cupo.')
    if day>today:raise ValidationError('La actividad no puede tener fecha futura.')
    if result is None:
        obj.cupo_diario_reservado=False
        return None
    old=(prior or {}).get('eligibilidad') or {}
    old_control=old.get('control_registro')
    was_candidate=old.get('potencialmente_puntuable',False)
    basic=result['potencialmente_puntuable']
    # Preserve an existing historical evaluation; no retrospective deadlines or evictions.
    if prior and old_control is None and (was_candidate or not basic):
        obj.cupo_diario_reservado=False
        return result
    initial=timezone.localtime(prior['creado'],TZ) if prior else now
    deadline=day+timedelta(days=2)
    control=deepcopy(old_control) if old_control else dict(version=1,zona_horaria='America/Santiago',dias_calendario=3,maximo_diario=MAXIMUM,
        fecha_realizacion=str(day),registrado_en=initial.isoformat(),fecha_registro=str(initial.date()),fecha_limite=str(deadline),registro_en_plazo=day<=initial.date()<=deadline)
    if not control['registro_en_plazo']:
        result['motivos'].append(LATE);basic=False
    elif basic and not was_candidate and today>deadline:
        result['motivos'].append(COMPLETED_LATE);basic=False
    if not basic:result.update(potencialmente_puntuable=False,estado='No elegible')
    count=used(obj.autor_id,day,obj.pk)
    retained=bool(prior and prior['reservado'] and was_candidate)
    blocked=bool(basic and count>=MAXIMUM and not retained)
    if blocked and not preview:raise ValidationError(FULL,code='cupo_diario')
    obj.cupo_diario_reservado=bool(basic and not blocked and not preview)
    control.update(reserva_cupo=obj.cupo_diario_reservado,cupo_usado_al_evaluar=count+(1 if obj.cupo_diario_reservado else 0),
        cupo_disponible_al_evaluar=max(0,MAXIMUM-count-(1 if obj.cupo_diario_reservado else 0)),
        bloqueada_por_cupo=blocked,requisitos_en_plazo=bool(basic),evaluado_en=now.isoformat())
    if blocked:control['mensaje_cupo']=FULL.replace('La actividad no se guardó;','Al guardar se bloqueará;')
    result['control_registro']=control
    return result
