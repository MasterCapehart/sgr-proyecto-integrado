from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import CierreCompromiso, AlertaLocal
from .operating_policy import current

def validate_transition(request,obj,before,data):
    if before is None:
        if obj.estado!='Ingresado':raise ValidationError('Un compromiso nuevo comienza Ingresado.')
        return
    old=before['estado']
    if old=='Realizado':raise ValidationError('El compromiso está cerrado. Usa la reapertura autorizada para modificarlo.')
    if old!=obj.estado and obj.estado not in current()['transiciones'].get(old,[]):raise ValidationError('La transición no está permitida por la política local vigente.')

def save_closure(request,obj,before,data):
    if obj.estado=='Realizado' and before and before['estado']!='Realizado':
        row=CierreCompromiso.objects.create(compromiso=obj,autor=request.user,fecha_plazo=obj.fecha_comprometida,dias_atraso=max(0,(timezone.localdate()-obj.fecha_comprometida).days),observacion=data['observacion'].strip())
        obj.cierre_actual=row;obj.save(update_fields=['cierre_actual'])
        AlertaLocal.objects.filter(recurso='compromisos',registro=obj.pk,activa=True).update(activa=False,resuelta_en=timezone.now())
