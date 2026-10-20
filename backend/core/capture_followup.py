"""Creación transaccional de un compromiso desde su atención o actividad."""
import hashlib,json
from django.core.exceptions import PermissionDenied,ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_GET
from . import local_api as api
from .models import Compromiso,Usuario,Atencion,Actividad


def fingerprint(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),cls=DjangoJSONEncoder).encode()).hexdigest()


def create(request,source,details,existing=None):
    if details is None:return None
    if not isinstance(details,dict) or not details:raise ValidationError('Completa los datos del nuevo compromiso.')
    if existing not in ('',None):raise ValidationError('Selecciona un compromiso existente o crea uno nuevo, no ambos.')
    if not api.allowed(request.user,'compromisos','crear'):raise PermissionDenied('No tienes permiso para crear compromisos en el tubo.')
    permitted={'descripcion','responsable','fecha_comprometida','sector','area_apoyo','origen'}
    if set(details)-permitted:raise ValidationError('El compromiso contiene campos no editables.')
    attention=isinstance(source,Atencion)
    cargo=request.user.cargo
    values=dict(descripcion=details.get('descripcion') or (source.descripcion if attention else source.solicitud),
                solicitante=source.solicitante if attention else source.contacto,
                sector=details.get('sector') or ('' if attention else source.sector),
                responsable=details.get('responsable',request.user.pk),fecha_comprometida=details.get('fecha_comprometida',''),
                area_apoyo=details.get('area_apoyo') or (cargo.area if cargo else ''),
                origen=details.get('origen','Externo' if attention else 'Interno'),
                fecha_solicitud=str(timezone.localdate() if attention else source.fecha),unidad=1)
    obj=Compromiso(autor=request.user,delegacion=api.active_delegation(request))
    from .domain_api import apply_fields
    apply_fields(request,'compromisos',obj,values)
    obj.save()
    from .auto_codes import operation_saved
    operation_saved(obj,'compromisos',request.user)
    return obj


def finish(request,commitment,source):
    if commitment is None:return
    code=source.folio if isinstance(source,Atencion) else source.codigo
    commitment.codigo_verificacion_foto=code
    commitment.save(update_fields=['codigo_verificacion_foto'])
    from .domain_api import representation
    after=representation(commitment)
    after.update(origen_tipo='atencion' if isinstance(source,Atencion) else 'actividad',origen_id=source.pk)
    api.record_event(request,'compromisos',commitment.pk,'crear',None,after)


@require_GET
def options(request):
    if not request.user.is_authenticated:return api.error('Inicia sesión.',401)
    if not api.allowed(request.user,'compromisos','crear') or not (api.allowed(request.user,'atenciones','crear') or api.allowed(request.user,'actividades','crear')):return api.error('No tienes permiso para registrar seguimiento.',403)
    d=api.active_delegation(request)
    if d is None:return api.error('Selecciona una delegación autorizada.',403)
    qs=Usuario.objects.filter(is_active=True).filter(Q(delegacion=d)|Q(delegaciones=d)).distinct()
    return api.ok(responsables=[{'id':u.pk,'nombre':u.get_full_name() or u.username} for u in qs])


@require_GET
def origins(request,pk):
    from .domain_api import gate,scoped
    denied=gate(request,'compromisos','ver')
    if denied:return denied
    obj=scoped(request,'compromisos').filter(pk=pk).first()
    if obj is None:return api.error('Compromiso no encontrado.',404)
    rows=[];d=api.active_delegation(request)
    if api.allowed(request.user,'actividades','ver'):
        for a in scoped(request,'actividades').filter(compromiso=obj)[:100]:rows.append(dict(tipo='actividad',id=a.pk,codigo=a.codigo,descripcion=a.solicitud,url='/pages/desempeno.html?registro='+str(a.pk)))
    if api.allowed(request.user,'atenciones','ver'):
        qs=Atencion.objects.filter(compromiso=obj).filter(Q(delegacion=d)|Q(delegacion_responsable=d)).order_by('pk')
        for a in qs[:100]:rows.append(dict(tipo='atencion',id=a.pk,codigo=a.folio,descripcion=a.descripcion,url='/pages/atencion-detalle.html?id='+str(a.pk)))
    return api.ok(results=rows)
