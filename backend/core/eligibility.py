"""Candidatura del bloque3. No otorga puntos ni aplica límites o plazos."""
import re
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import ReglaActividad,Usuario,ItemMeta

def local_users(delegation):
    return Usuario.objects.filter(is_active=True).filter(Q(delegacion=delegation)|Q(delegaciones=delegation)).distinct()

def rule_data(rule):
    if not rule:return None
    return dict(id=rule.pk,version=rule.version,item=rule.item_id,clasificacion=rule.clasificacion,valida_para_puntuar=rule.valida_para_puntuar,motivo=rule.motivo,creado=rule.creado.isoformat())

def current(delegation,item):
    return ReglaActividad.objects.filter(delegacion=delegation,item_id=item).first()

def phone_valid(phone):
    return bool(re.fullmatch(r'\+?[0-9 ()-]{8,20}',phone or '') and 8<=len(re.sub(r'\D','',phone or ''))<=15)

def assess(contact,phone,rule,beneficiary):
    kind=rule['clasificacion'] if rule else 'Sin definir'
    reasons=[]
    if beneficiary.get('es_delegado'):
        kind='Otra gestión';reasons.append('El beneficiario es el delegado: Otra gestión sin puntaje.')
    if not rule:reasons.append('El tipo de actividad no tiene una regla de clasificación configurada.')
    elif rule['clasificacion']=='Coordinación':reasons.append('Las gestiones de coordinación no generan puntaje.')
    elif rule['clasificacion']=='Otra gestión':reasons.append('Otra gestión no genera puntaje.')
    elif not rule['valida_para_puntuar']:reasons.append('La ejecución no está habilitada como válida en el catálogo.')
    if not (contact or '').strip():reasons.append('Falta el nombre del vecino o usuario beneficiario.')
    if not phone_valid(phone):reasons.append('Falta un teléfono válido del vecino o usuario (8 a 15 dígitos).')
    candidate=not reasons
    return dict(modelo=1,regla=rule,clasificacion=kind,beneficiario=beneficiary,potencialmente_puntuable=candidate,
        estado='Potencialmente puntuable' if candidate else 'No elegible',motivos=reasons,
        alcance='Clasificación preliminar: no otorga puntos ni confirma cumplimiento de metas.')

def beneficiary_data(obj,old):
    identifier=obj.beneficiario_usuario_id
    rut=obj.rut_contacto or ''
    prior=(old or {}).get('beneficiario',{})
    if old and prior.get('usuario')==identifier and prior.get('rut_contacto','')==rut:return prior
    person=obj.beneficiario_usuario if identifier else None
    delegate=bool(person and person.rol_id and person.rol.nombre.strip().casefold()=='delegado')
    matched=None
    if rut:
        from .neighbors import normalize_rut
        for user in local_users(obj.delegacion).exclude(rut__isnull=True).select_related('rol'):
            if not user.rol_id or user.rol.nombre.strip().casefold()!='delegado':continue
            try:normalized=normalize_rut(user.rut)
            except ValidationError:continue
            if normalized==rut:matched=user;delegate=True;break
    return dict(usuario=identifier,nombre=(person.get_full_name() or person.username) if person else '',rut_contacto=rut,
        es_delegado=delegate,identificado_por='Cuenta municipal' if person else 'RUN de delegado' if matched else 'Datos del contacto')

def evaluate_activity(obj,force=False,preview=False):
    old=obj.elegibilidad_snapshot
    if obj.pk and old is None and not force:return None
    same=bool(old and (old.get('regla') or {}).get('item',old.get('item'))==obj.item_id)
    if same:
        rule=old.get('regla')
    else:
        # Publication and capture serialize on the item, fixing the rule version used.
        if not preview:ItemMeta.objects.select_for_update().get(pk=obj.item_id)
        rule=rule_data(current(obj.delegacion,obj.item_id))
    result=assess(obj.contacto,obj.telefono,rule,beneficiary_data(obj,old));result.update(item=obj.item_id,evaluado_en=timezone.now().isoformat())
    return result

def legacy_attention(obj):
    result=assess(obj.solicitante,obj.telefono_solicitante,None,dict(es_delegado=False))
    result['motivos'].insert(0,'Atención independiente sin un tipo de actividad vinculado.')
    return result

def display(obj):
    if obj.elegibilidad_snapshot is not None:
        result=dict(obj.elegibilidad_snapshot)
        result['alcance']='Clasificación preliminar: no otorga puntos ni confirma cumplimiento de metas.'
        return result
    return dict(modelo=1,regla=None,clasificacion='Sin definir',potencialmente_puntuable=False,estado='Sin evaluación histórica',motivos=['Registro anterior sin clasificación capturada. No se presume elegibilidad.'],alcance='No otorga puntos.')
