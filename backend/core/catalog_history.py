"""Captura etiquetas al registrar. Las capturas tardías nunca se hacen pasar por originales."""
from django.utils import timezone
from .models import VersionCatalogo, Atencion, Actividad
CATALOGS={'periodos','delegaciones','cargos','items-metas','tipos-atencion','subatenciones'}

def catalog(obj):
    fields=['id','version','codigo','nombre','descripcion','area','comuna','direccion','unidad_medida','estado','tipo_atencion_id','planilla','fecha_inicio','fecha_fin','cerrado','parametros_cierre']
    data={k:(getattr(obj,k).isoformat() if hasattr(getattr(obj,k),'isoformat') else getattr(obj,k)) for k in fields if hasattr(obj,k)}
    if hasattr(obj,'cargos'):
        data['cargos']=list(obj.cargos.values_list('pk',flat=True))
        data['cargos_detalle']=list(obj.cargos.values('id','nombre','version','area'))
    return data

def attention(obj,observed=False):
    return {'tipo_atencion':catalog(obj.tipo_atencion),'sub_atencion':catalog(obj.sub_atencion),'delegacion':catalog(obj.delegacion),'capturado_en':timezone.now().isoformat(),'observada':observed}

def activity(obj,observed=False):
    return {'item':catalog(obj.item),'cargo':catalog(obj.cargo) if obj.cargo_id else None,'delegacion':catalog(obj.delegacion),'capturado_en':timezone.now().isoformat(),'observada':observed}

def record(request,resource,obj,observed=False):
    if resource in CATALOGS:
        VersionCatalogo.objects.get_or_create(recurso=resource,registro=obj.pk,version=obj.version,defaults={'datos':catalog(obj),'autor':request.user,'observada':observed})

def freeze_references(resource,obj):
    if resource not in CATALOGS:return
    attention_filters={'tipos-atencion':{'tipo_atencion':obj},'subatenciones':{'sub_atencion':obj},'delegaciones':{'delegacion':obj}}
    activity_filters={'items-metas':{'item':obj},'cargos':{'cargo':obj},'delegaciones':{'delegacion':obj}}
    if resource in attention_filters:
        for entry in Atencion.objects.filter(catalogos_snapshot__isnull=True,**attention_filters[resource]).select_related('tipo_atencion','sub_atencion','delegacion'):
            Atencion.objects.filter(pk=entry.pk,catalogos_snapshot__isnull=True).update(catalogos_snapshot=attention(entry,True))
    if resource in activity_filters:
        for entry in Actividad.objects.filter(catalogos_snapshot__isnull=True,**activity_filters[resource]).select_related('item','cargo','delegacion'):
            Actividad.objects.filter(pk=entry.pk,catalogos_snapshot__isnull=True).update(catalogos_snapshot=activity(entry,True))
