"""Conteos operativos autorizados; no calcula desempeño ni cumplimiento de metas."""
from datetime import datetime, time, timedelta
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from . import local_api as api

def card(key,label,value,tone='neutral',help=''):
    return dict(key=key,label=label,value=value,tone=tone,help=help)

def resource_kpis(qs,resource):
    # Se recibe el mismo QuerySet filtrado del listado, antes de paginar.
    def count(condition=None):return Count('pk',filter=condition,distinct=True)
    if resource=='actividades':
        v=qs.aggregate(total=count(),pendientes=count(Q(estado='Pendiente')),validadas=count(Q(estado='Validada')),devueltas=count(Q(estado__in=['Corrección','Rechazada'])))
        cards=[card('total','Actividades registradas',v['total']),card('pendientes','Pendientes de validación',v['pendientes'],'warning'),card('validadas','Actividades validadas',v['validadas'],'success'),card('devueltas','Devueltas para revisión',v['devueltas'],'warning')]
    elif resource=='compromisos':
        v=qs.aggregate(total=count(),en_curso=count(Q(estado__in=['Pendiente','En proceso'])),realizados=count(Q(estado='Realizado')),vencidos=count(Q(fecha_comprometida__lt=timezone.localdate())&~Q(estado='Realizado')))
        cards=[card('total','Compromisos registrados',v['total']),card('en_curso','Pendientes / en proceso',v['en_curso'],'info'),card('realizados','Compromisos realizados',v['realizados'],'success'),card('vencidos','Compromisos vencidos',v['vencidos'],'danger',help='Plazo anterior a hoy y aún sin realizar.')]
    elif resource=='evidencias':
        v=qs.aggregate(total=count(),pendientes=count(Q(estado='Pendiente')),aprobadas=count(Q(estado='Aprobada')),devueltas=count(Q(estado__in=['Corrección','Rechazada'])),anuladas=count(Q(estado='Anulada')))
        cards=[card('total','Evidencias registradas',v['total'],help=f"Incluye versiones; {v['anuladas']} anuladas."),card('pendientes','Pendientes de revisión',v['pendientes'],'warning'),card('aprobadas','Evidencias aprobadas',v['aprobadas'],'success'),card('devueltas','Corrección / rechazadas',v['devueltas'],'warning')]
    elif resource=='atenciones':
        today=timezone.localdate()
        # Límites conscientes de zona; no depende de tablas horarias instaladas en MySQL.
        start=timezone.make_aware(datetime.combine(today.replace(day=1),time.min))
        end=timezone.make_aware(datetime.combine(today+timedelta(days=1),time.min))
        v=qs.aggregate(total=count(),mes=count(Q(fecha_registro__gte=start,fecha_registro__lt=end)),tipos=Count('tipo_atencion_id',distinct=True),casos=Count('caso_social',filter=~Q(caso_social=''),distinct=True))
        cards=[card('total','Atenciones registradas',v['total']),card('mes','Atenciones de este mes',v['mes'],'info',help='Desde el día 1 hasta hoy.'),card('tipos','Tipos de atención utilizados',v['tipos']),card('casos','Casos sociales registrados',v['casos'],help='Códigos de caso distintos; no equivale a personas únicas.')]
    else:return None
    return dict(cards=cards,generated_at=timezone.now().isoformat(),scope='Todos los resultados de los filtros aplicados, no solo esta página.')

@require_http_methods(['GET'])
def overview(request):
    from . import domain_api as domain
    from .models import Atencion
    if not request.user.is_authenticated:return api.error('Inicia sesión.',401)
    if api.active_delegation(request) is None:return api.error('Selecciona una delegación autorizada.',403)
    cards=[]
    if api.allowed(request.user,'atenciones','ver'):
        d=api.active_delegation(request)
        total=Atencion.objects.filter(Q(delegacion=d)|Q(delegacion_responsable=d),estado=True).count()
        cards.append(card('atenciones','Atenciones ciudadanas',total,help='Registros activos del contexto autorizado.'))
    if api.allowed(request.user,'actividades','ver'):
        cards.append(card('actividades','Actividades registradas',domain.scoped(request,'actividades').count(),help='Según tu permiso de consulta.'))
    if api.allowed(request.user,'compromisos','ver'):
        v=domain.scoped(request,'compromisos').aggregate(abiertos=Count('pk',filter=~Q(estado='Realizado')),vencidos=Count('pk',filter=Q(fecha_comprometida__lt=timezone.localdate())&~Q(estado='Realizado')))
        cards.extend([card('abiertos','Compromisos abiertos',v['abiertos'],'info'),card('vencidos','Compromisos vencidos',v['vencidos'],'danger',help='Plazo anterior a hoy y aún sin realizar.')])
    return api.ok(dict(cards=cards,generated_at=timezone.now().isoformat(),scope='Delegación activa · historial disponible según tus permisos.'))
