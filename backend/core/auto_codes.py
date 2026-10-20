"""Identificadores nuevos, estables y asignados dentro de la transacción de alta.

Prefijos operativos extraídos del Excel; año/separadores/PK son adaptación web.
Los consecutivos son PK por tabla, no números de filas ni secuencias sin saltos.
"""
import uuid
from django.db import IntegrityError, transaction
from django.utils import timezone

PREFIXES={'delegaciones':'DEL','cargos':'CAR','items-metas':'ITM','tipos-atencion':'TIP','subatenciones':'SUB','periodos':'PER'}
AREA_PREFIXES={'APOYO ADMINISTRATIVO':'APA','COOR SERV. COMU':'COS','PLANIFICACIÓN Y GESTIÓN':'PYG',**{f'TERRITORIAL OO.CC. {i}':f'COM{i}' for i in range(1,5)},**dict(zip([f'GESTOR SOCIAL {i}' for i in range(1,6)],['SOC','SOC2','SCO3','SCO4','SOC5']))}
PROFILE_PREFIXES={'AP_ADM':'APA','COOR_DISERCO':'COS','PLAN_CON':'PYG','GES_SEG':'SEG'}

def prepare_catalog(obj,incoming,resource,creating,request=None):
    token=incoming.pop('_reserva_codigo',None)
    if token is not None:
        from django.core.exceptions import ValidationError
        from .code_reservation import use
        if not creating or resource not in PREFIXES:raise ValidationError('La reserva solo se utiliza para crear un catálogo.')
        event=use(request,resource,token)
        if incoming.get('codigo') not in (None,'',event.despues['codigo']):raise ValidationError('El código no coincide con la reserva.')
        incoming['codigo']=event.despues['codigo'];obj._code_reservation=event
        return
    if creating and resource in PREFIXES and (incoming.get('codigo') is None or isinstance(incoming.get('codigo'),str) and not incoming['codigo'].strip()):
        incoming['codigo']='TMP-'+uuid.uuid4().hex[:16]
        obj._automatic_code=True


def assign(obj,field,prefix,day=None):
    stamp=day.strftime('%Y%m%d')+'-' if day else ''
    candidate=f'{prefix}-{stamp}{obj.pk:06d}'
    limit=obj._meta.get_field(field).max_length
    for attempt in range(6):
        value=candidate if attempt==0 else candidate[:limit-9]+'-'+uuid.uuid4().hex[:8].upper()
        try:
            with transaction.atomic():
                type(obj).objects.filter(pk=obj.pk).update(**{field:value})
            setattr(obj,field,value)
            return value
        except IntegrityError:
            if attempt==5:raise


def catalog_saved(obj,resource):
    event=getattr(obj,'_code_reservation',None)
    if event is not None:
        event.despues['consumido']=True;event.registro=obj.pk;event.save(update_fields=['despues','registro'])
    if getattr(obj,'_automatic_code',False):assign(obj,'codigo',PREFIXES[resource])


def area_prefix(cargo):
    return (AREA_PREFIXES.get(cargo.nombre) or PROFILE_PREFIXES.get(cargo.planilla) or 'ACT') if cargo else 'ACT'


def operation_saved(obj,resource,user):
    if resource=='actividades':assign(obj,'codigo',area_prefix(obj.cargo),obj.fecha)
    if resource=='compromisos':
        day=obj.fecha_solicitud or timezone.localdate()
        assign(obj,'folio','TUB',day)
        if not obj.codigo_verificacion_foto:assign(obj,'codigo_verificacion_foto','FOTO',day)
