"""Reserva de código visible antes del alta, sin actividades ficticias."""
from datetime import date
import uuid
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST
from . import local_api as api,domain_api as domain
from .models import Actividad,EventoLocal
from .auto_codes import area_prefix
from .code_reservation import SALT,use

RESOURCE='captura_actividad'

@require_POST
def reserve(request):
 denied=domain.gate(request,'actividades','crear')
 if denied:return denied
 try:
  data=api.body(request)
  if set(data)-{'fecha'} or not isinstance(data.get('fecha'),str):raise ValidationError('Indica la fecha del registro.')
  day=date.fromisoformat(data['fecha'])
  if day>timezone.localdate():raise ValidationError('La fecha no puede estar en el futuro.')
  with transaction.atomic():
   event=EventoLocal.objects.create(usuario=request.user,delegacion=api.active_delegation(request),recurso='reserva_codigo',accion='reservar',despues={'recurso':RESOURCE,'fecha':str(day),'cargo':request.user.cargo_id,'consumido':False})
   prefix=area_prefix(request.user.cargo)+'-'+day.strftime('%Y%m%d')+'-R'
   code=prefix+f'{event.pk:06d}'
   while Actividad.objects.filter(codigo=code).exists():code=prefix+uuid.uuid4().hex[:10].upper()
   event.despues['codigo']=code;event.save(update_fields=['despues'])
   token=signing.dumps({'id':event.pk},salt=SALT)
  response=api.ok({'codigo':code,'reserva':token});response['Cache-Control']='private, no-store';return response
 except (ValueError,TypeError,ValidationError) as ex:return api.error('; '.join(ex.messages) if isinstance(ex,ValidationError) else 'Fecha inválida.')

def apply(request,obj,token):
 event=use(request,RESOURCE,token)
 if event.despues.get('fecha')!=str(obj.fecha) or event.despues.get('cargo')!=request.user.cargo_id:raise ValidationError('La fecha o el cargo cambiaron. Solicita nuevamente el código.')
 obj.codigo=event.despues['codigo']
 return event
