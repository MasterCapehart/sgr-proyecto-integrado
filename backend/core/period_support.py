"""Reglas de calendario y protección de parámetros, sin motor de cálculos."""
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import PeriodoGestion, ConfiguracionMeta


def lock_meta_periods(qs, pk, data):
    """Orden común con cierre: período(s), meta, ítem. Devuelve IDs bloqueados."""
    ids=set()
    if pk:
        old=qs.filter(pk=pk).values_list('periodo_gestion_id',flat=True).first()
        if old:ids.add(old)
    incoming=data.get('periodo_gestion')
    if incoming is not None and not isinstance(incoming,bool) and str(incoming).isdigit():ids.add(int(incoming))
    if not incoming and isinstance(data.get('periodo'),str):
        ids.update(PeriodoGestion.objects.filter(Q(codigo__iexact=data['periodo'].strip())|Q(nombre__iexact=data['periodo'].strip())).values_list('pk',flat=True))
    list(PeriodoGestion.objects.select_for_update().filter(pk__in=ids).order_by('pk'))
    return ids


def prepare_meta(obj,incoming,creating):
    if obj.pk:
        old=ConfiguracionMeta.objects.get(pk=obj.pk)
        if old.conciliada_con_id:raise ValidationError('Configuración conciliada: consulta la configuración vigente indicada; no se modifica el histórico.')
        if old.periodo_gestion_id and PeriodoGestion.objects.get(pk=old.periodo_gestion_id).cerrado:
            raise ValidationError('El período está cerrado. Se requiere una reapertura autorizada antes de modificar sus metas.')
    if 'periodo' in incoming and 'periodo_gestion' not in incoming:
        text=incoming['periodo']
        if not isinstance(text,str):raise ValidationError({'periodo':'Selecciona un período registrado.'})
        matches=PeriodoGestion.objects.filter(Q(codigo__iexact=text.strip())|Q(nombre__iexact=text.strip()))
        if matches.count()!=1:raise ValidationError({'periodo':'Selecciona un período registrado. Los históricos no requieren inventar fechas.'})
        incoming['periodo_gestion']=matches.first().pk
    if creating and not incoming.get('periodo_gestion'):
        raise ValidationError({'periodo_gestion':'Selecciona un período registrado.'})
    if obj.periodo_gestion_id and 'periodo_gestion' in incoming and incoming['periodo_gestion'] in [None,'']:
        raise ValidationError({'periodo_gestion':'No se puede quitar el período de una configuración vinculada.'})


def validate_period_meta(obj):
    if obj.periodo_gestion_id:
        period=PeriodoGestion.objects.get(pk=obj.periodo_gestion_id)
        if period.cerrado or not period.estado:raise ValidationError('El período debe estar activo y abierto para configurar metas.')
        obj.periodo=period.codigo
