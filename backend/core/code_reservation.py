"""Reserva auditable de códigos, sin crear filas ficticias en los catálogos."""
import uuid
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.views.decorators.http import require_POST
from . import local_api as api
from .auto_codes import PREFIXES
from .models import EventoLocal

SALT='sgr.catalog-code-reservation.v1'

@require_POST
def reserve(request,resource):
    if not request.user.is_authenticated:return api.error('Inicia sesión.',401)
    if resource not in PREFIXES:return api.error('Este catálogo no utiliza reserva de código.',404)
    if not api.allowed(request.user,resource,'crear'):return api.error('No tienes permiso para crear registros.',403)
    delegation=api.active_delegation(request)
    if delegation is None:return api.error('Selecciona una delegación autorizada.',403)
    with transaction.atomic():
        event=EventoLocal.objects.create(usuario=request.user,delegacion=delegation,recurso='reserva_codigo',accion='reservar',despues={'recurso':resource,'consumido':False})
        # R separa la secuencia de reservas de los códigos antiguos basados en PK.
        code=f'{PREFIXES[resource]}-R{event.pk:06d}'
        model=api.RESOURCES[resource][0]
        while model.objects.filter(codigo__iexact=code).exists():code=PREFIXES[resource]+'-R'+uuid.uuid4().hex[:12].upper()
        event.despues.update(codigo=code);event.save(update_fields=['despues'])
        token=signing.dumps({'id':event.pk},salt=SALT)
    response=api.ok({'codigo':code,'reserva':token})
    response['Cache-Control']='private, no-store'
    return response


def use(request,resource,token):
    if not isinstance(token,str) or len(token)>512:
        raise ValidationError('La reserva del código no es válida.')
    try:
        payload=signing.loads(token,salt=SALT,max_age=86400)
        event=EventoLocal.objects.select_for_update().get(pk=payload['id'],usuario=request.user,recurso='reserva_codigo')
    except (signing.BadSignature,EventoLocal.DoesNotExist,KeyError,TypeError,ValueError):
        raise ValidationError('La reserva del código no es válida o venció. Abre nuevamente el formulario.')
    if event.delegacion_id!=getattr(api.active_delegation(request),'pk',None) or event.despues.get('recurso')!=resource or event.despues.get('consumido'):
        raise ValidationError('La reserva no corresponde a este formulario o ya fue utilizada.')
    return event
