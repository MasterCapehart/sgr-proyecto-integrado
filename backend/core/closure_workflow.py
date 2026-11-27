from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import CierreCompromiso, AlertaLocal
from .operating_policy import current
from .tracking import TERMINAL

def validate_transition(request,obj,before,data):
 if before is None:
  if obj.estado not in ('Pendiente','Ingresado'):raise ValidationError('Un compromiso nuevo comienza Pendiente.')
  return
 old=before['estado']
 if old in TERMINAL:raise ValidationError('El compromiso está cerrado. Usa la reapertura autorizada para modificarlo.')
 if old!=obj.estado and obj.estado not in current()['transiciones'].get(old,[]):raise ValidationError('La transición no está permitida por la política vigente.')
 if obj.estado in TERMINAL and not obj.resultado.strip():raise ValidationError('Indica el resultado o motivo de cierre del compromiso.')

def save_closure(request,obj,before,data):
 if obj.estado in TERMINAL and before and before['estado'] not in TERMINAL:
  row=CierreCompromiso.objects.create(compromiso=obj,autor=request.user,fecha_plazo=obj.fecha_comprometida,dias_atraso=max(0,(timezone.localdate()-obj.fecha_comprometida).days),observacion=data['observacion'].strip())
  obj.cierre_actual=row;obj.fecha_cierre=timezone.now();obj.save(update_fields=['cierre_actual','fecha_cierre'])
  AlertaLocal.objects.filter(recurso='compromisos',registro=obj.pk,activa=True).update(activa=False,resuelta_en=timezone.now())
