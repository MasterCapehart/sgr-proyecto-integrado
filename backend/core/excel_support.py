"""Datos y presentación tomados de las columnas de las planillas de referencia."""
import re
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import ItemMeta

SOCIAL_FIELDS = ['rut_solicitante','telefono_solicitante','requiere_visita','fecha_visita','fecha_entrega_informe','fecha_entrega_beneficio','gestion_realizada','fecha_visita_programada','fecha_visita_realizada','tipo_gestion']

def items_for(user):
    qs=ItemMeta.objects.filter(estado=True)
    if not user.is_superuser:
        qs=qs.filter(Q(cargos=user.cargo_id)|Q(cargos__isnull=True)).distinct() if user.cargo_id else qs.filter(cargos__isnull=True)
    return qs

def validate_social(obj,data):
    for field in SOCIAL_FIELDS:
        if field not in data:continue
        value=data[field]
        if field=='requiere_visita':
            if not isinstance(value,bool):raise ValidationError('Indica Sí o No en requiere visita.')
        elif field.startswith('fecha_'):
            if value in ['',None]:value=None
            elif not isinstance(value,str):raise ValidationError('Fecha de gestión inválida.')
            else:
                try:value=date.fromisoformat(value)
                except ValueError:raise ValidationError('Fecha de gestión inválida.')
        else:
            if not isinstance(value,str):raise ValidationError('Los datos del solicitante y la gestión deben ser texto.')
            value=value.strip()
        setattr(obj,field,value)
    if obj.telefono_solicitante and not re.fullmatch(r'\+?[0-9 ()-]{8,20}',obj.telefono_solicitante):raise ValidationError('Teléfono del solicitante inválido.')
    if obj.rut_solicitante:
        rut=re.sub(r'[.\s]','',obj.rut_solicitante).upper()
        if not re.fullmatch(r'\d{7,8}-[0-9K]',rut):raise ValidationError('RUN inválido. Usa número y dígito verificador.')
        number,digit=rut.split('-');total=sum(int(n)*(2+i%6) for i,n in enumerate(reversed(number)));expected=11-total%11;expected='0' if expected==11 else 'K' if expected==10 else str(expected)
        if digit!=expected:raise ValidationError('El dígito verificador del RUN no es válido.')
        obj.rut_solicitante=rut
    if (obj.fecha_visita_programada or obj.fecha_visita_realizada) and not obj.requiere_visita:raise ValidationError('Indica que requiere visita antes de informar sus fechas.')
    if obj.fecha_visita_realizada and obj.fecha_visita_realizada>timezone.localdate():raise ValidationError('La visita realizada no puede estar en el futuro.')
    if obj.fecha_visita and not obj.requiere_visita:raise ValidationError('Indica que requiere visita antes de programar su fecha.')
    if obj.fecha_entrega_informe and obj.fecha_entrega_beneficio and obj.fecha_entrega_beneficio<obj.fecha_entrega_informe:raise ValidationError('La entrega del beneficio no puede preceder al informe registrado en esta gestión.')

EXCEL_COLUMNS={
 'actividades': [('id','N°'),('fecha','Fecha'),('solicitud','Actividad / solicitud / problema'),('accion','Acción / detalle'),('contacto','Nombre de contacto'),('telefono','Teléfono'),('ingreso_tubo','Ingreso al tubo'),('item_nombre','Ítem'),('derivado_a','Derivado a'),('estado_derivacion','Estado derivación'),('codigo','Código de evidencia'),('imagen_verificacion','Imagen / archivo verificador'),('estado','Verificación'),('cargo_nombre','Cargo'),('area','Área'),('autor_nombre','Funcionario')],
 'compromisos':[('id','N°'),('fecha_solicitud','Fecha solicitud'),('descripcion','Actividad / solicitud / problema'),('origen','INT / EXT'),('solicitante','Solicitante'),('sector','Territorio'),('responsable_nombre','Responsable'),('fecha_comprometida','Fecha compromiso'),('mes_compromiso','Mes'),('area_apoyo','Área / persona de apoyo'),('ultima_observacion','Avance / observaciones'),('estado','Estatus'),('unidad','Unidad'),('codigo_verificacion_foto','Código verificación foto'),('folio','Folio')],
 'evidencias':[('id','N°'),('codigo_actividad','Código actividad'),('nombre_archivo','Archivo'),('descripcion','Descripción'),('estado','Revisión'),('autor_nombre','Autor'),('creado','Fecha registro')],
}

COLUMN_FILTERS={
 'actividades':{'id':'id','fecha':'fecha','solicitud':'solicitud__icontains','accion':'accion__icontains','contacto':'contacto__icontains','telefono':'telefono__icontains','item_nombre':'item__nombre__icontains','derivado_a':'derivado_a__icontains','codigo':'codigo__icontains','estado':'estado__icontains','cargo_nombre':'cargo__nombre__icontains','autor_nombre':'autor__first_name__icontains'},
 'compromisos':{'id':'id','fecha_solicitud':'fecha_solicitud','descripcion':'descripcion__icontains','origen':'origen__icontains','solicitante':'solicitante__icontains','sector':'sector__icontains','responsable_nombre':'responsable__first_name__icontains','fecha_comprometida':'fecha_comprometida','mes_compromiso':'fecha_comprometida__month','area_apoyo':'area_apoyo__icontains','estado':'estado__icontains'},
 'evidencias':{'codigo_actividad':'actividad__codigo__icontains','nombre_archivo':'nombre_archivo__icontains','descripcion':'descripcion__icontains','estado':'estado__icontains'},
}

GESTIONES={1:['1RA GESTION','ATENCIÓN SOCIAL A USUARIO PRESENCIAL','ENTREGA INFORME','EMERGENCIA','VISITA TERRENO','OTRAS GESTIONES'],2:['2DA GESTION','ENTREGA BENEFICIO','ENTREGA INFORME','VISITA TERRENO','EMERGENCIA','OTROS'],3:['3RA GESTION','ENTREGA BENEFICIO','ENTREGA INFORME','EMERGENCIA','OTROS']}
def validate_stage(obj):
    if obj.tipo_gestion and (not obj.caso_social or obj.tipo_gestion not in GESTIONES.get(obj.numero_gestion,[])):
        raise ValidationError('El tipo de gestión no corresponde a esta etapa del caso social.')
