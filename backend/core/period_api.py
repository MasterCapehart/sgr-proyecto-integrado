"""Cierre/reapertura con autorización, motivo, versiones y captura de parámetros."""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import PeriodoGestion
from . import local_api as api, catalog_history


@require_http_methods(['POST'])
def transition(request,pk,action):
    if not request.user.is_authenticated:return api.error('Inicia sesión.',401)
    if not api.allowed(request.user,'periodos',action):return api.error('No tienes permiso para esta operación.',403)
    try:
        data=api.body(request);motivo=data.get('motivo')
        if set(data)-{'_version','motivo'}:raise ValidationError('Campos no permitidos.')
        if not isinstance(motivo,str) or not motivo.strip() or len(motivo)>2000:raise ValidationError('Indica un motivo de hasta 2000 caracteres.')
        with transaction.atomic():
            p=PeriodoGestion.objects.select_for_update().filter(pk=pk).first()
            if not p:return api.error('Período no encontrado.',404)
            expected=data.get('_version')
            if expected is None:return api.error('Falta la versión del período.',428)
            if isinstance(expected,bool) or not isinstance(expected,int) or expected!=p.version:return api.error('El período cambió. Recarga antes de continuar.',409)
            closing=action=='cerrar'
            if p.cerrado==closing:return api.error('El período ya está en ese estado.',409)
            if closing and not p.estado:raise ValidationError('Activa el período antes de cerrarlo.')
            before=api.snapshot(p,api.RESOURCES['periodos'][1]);catalog_history.record(request,'periodos',p)
            if closing:
                metas=list(p.metas.select_for_update().filter(conciliada_con__isnull=True).order_by('pk'))
                p.parametros_cierre={'capturado_en':timezone.now().isoformat(),'metas':[{'id':m.pk,'version':m.version,'item':m.item_id,'cargo':m.cargo_id,'cargo_nombre':m.cargo.nombre if m.cargo_id else None,'item_nombre':m.item.nombre,'meta_esperada':str(m.meta_esperada),'ponderacion':str(m.ponderacion),'estado':m.estado} for m in metas],'alcance':'Parámetros conservados; no incluye resultados de un motor de cálculo.'}
            if closing:
                from .absences import closure
                p.parametros_cierre['ajustes_ausencia']=closure(p)
            p.cerrado=closing;p.version+=1;p.full_clean();p.save()
            catalog_history.record(request,'periodos',p)
            after=api.snapshot(p,api.RESOURCES['periodos'][1]);api.record_event(request,'periodos',p.pk,action,before,{**after,'motivo':motivo.strip()})
        return api.ok(after,message='Período cerrado.' if closing else 'Período reabierto con auditoría.')
    except (ValidationError,ValueError,TypeError) as exc:return api.error('; '.join(exc.messages) if isinstance(exc,ValidationError) else 'Solicitud inválida.')
