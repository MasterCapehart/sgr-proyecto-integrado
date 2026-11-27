"""Folio interno reservado al abrir; una reserva no crea una carta."""
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST
from . import local_api as api,domain_api as domain
from .models import EventoLocal
SALT='sgr.letter-reservation.v1'
@require_POST
def reserve(request):
 denied=domain.gate(request,'cartas','crear')
 if denied:return denied
 with transaction.atomic():
  e=EventoLocal.objects.create(usuario=request.user,delegacion=api.active_delegation(request),recurso='reserva_carta',accion='reservar',despues={'consumido':False})
  code=f'CAR-{timezone.localdate().year}-R{e.pk:06d}'
  e.despues['codigo']=code;e.save(update_fields=['despues'])
  token=signing.dumps({'id':e.pk},salt=SALT)
 r=api.ok({'codigo':code,'reserva':token});r['Cache-Control']='private, no-store';return r

def use(request,token):
 if not isinstance(token,str) or len(token)>512:raise ValidationError('Reserva de folio inválida.')
 try:
  value=signing.loads(token,salt=SALT,max_age=86400)
  e=EventoLocal.objects.select_for_update().get(pk=value['id'],usuario=request.user,recurso='reserva_carta')
 except (signing.BadSignature,EventoLocal.DoesNotExist,KeyError,TypeError,ValueError):raise ValidationError('El folio reservado no es válido o venció. Abre nuevamente el formulario.')
 if e.delegacion_id!=api.active_delegation(request).pk or e.despues.get('consumido'):raise ValidationError('El folio pertenece a otro contexto o ya fue utilizado.')
 return e
