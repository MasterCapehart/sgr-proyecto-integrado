"""Resumen personal de lectura; no calcula metas ni altera permisos existentes."""
import calendar
import re
from datetime import date, datetime, time, timedelta
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.http import require_GET
from . import local_api as api, domain_api as domain
from .models import Atencion


def bounds(day):
    return timezone.make_aware(datetime.combine(day, time.min))


def task(kind, obj, title, url, priority, due=None):
    return dict(kind=kind, id=obj.pk, title=title, url=url, priority=priority,
                due=due.isoformat() if due else None)


@require_GET
def overview(request):
    user = request.user
    if not user.is_authenticated or not user.is_active:
        return api.error('Inicia sesión.', 401)
    if not user.is_superuser and (not user.rol_id or not user.rol.estado):
        return api.error('Tu rol no está habilitado.', 403)
    delegation = api.active_delegation(request)
    if delegation is None:
        return api.error('Selecciona una delegación autorizada.', 403)
    today = timezone.localdate()
    period = request.GET.get('mes', today.strftime('%Y-%m'))
    if not re.fullmatch(r'\d{4}-\d{2}', period):
        return api.error('Selecciona un mes válido con formato AAAA-MM.')
    try:
        year, month = map(int, period.split('-'))
        start = date(year, month, 1)
        if not 2000 <= year <= 2100 or start > today:
            raise ValueError
        days = calendar.monthrange(year, month)[1]
        end = start + timedelta(days=days)
    except ValueError:
        return api.error('Selecciona un mes válido que no sea futuro.')

    def allowed(resource, action='ver'):
        return api.allowed(user, resource, action)

    activities = domain.scoped(request, 'actividades').filter(autor=user) if allowed('actividades') else None
    commitments = domain.scoped(request, 'compromisos').filter(responsable=user) if allowed('compromisos') else None
    evidence = domain.scoped(request, 'evidencias').filter(actividad__autor=user, siguiente_version__isnull=True).exclude(estado='Anulada') if allowed('evidencias') else None
    attentions = Atencion.objects.filter(Q(delegacion=delegation) | Q(delegacion_responsable=delegation), usuario=user, estado=True) if allowed('atenciones') else None

    def monthly(qs, field='creado'):
        return qs.filter(**{field+'__gte': bounds(start), field+'__lt': bounds(end)})

    month_data = dict(attentions=None, activities=None, commitments=None, evidence=None)
    if attentions is not None:
        month_data['attentions'] = monthly(attentions, 'fecha_registro').count()
    if activities is not None:
        month_data['activities'] = monthly(activities).count()
    if commitments is not None:
        v = monthly(commitments).aggregate(total=Count('pk'), closed=Count('pk', filter=Q(estado='Realizado')))
        month_data['commitments'] = dict(v, percent=round(v['closed'] * 100 / v['total']) if v['total'] else None)
    if evidence is not None:
        month_data['evidence'] = monthly(evidence).aggregate(
            approved=Count('pk', filter=Q(estado='Aprobada')),
            waiting=Count('pk', filter=Q(estado='Pendiente')),
            correction=Count('pk', filter=Q(estado__in=['Corrección', 'Rechazada'])))

    weeks = []
    for day in range(1, days+1, 7):
        a, b = start + timedelta(days=day-1), start + timedelta(days=min(day+6, days))
        def count(qs, field):
            return qs.filter(**{field+'__gte': bounds(a), field+'__lt': bounds(b)}).count() if qs is not None else None
        weeks.append(dict(label=f'{day}–{min(day+6, days)}',
                          attentions=count(attentions, 'fecha_registro'), activities=count(activities, 'creado')))

    pending = dict(commitments=None, overdue=None, correction=None, review=None, drafts=None, waiting=None, activity_correction=None)
    tasks = []
    if commitments is not None:
        opened = commitments.exclude(estado='Realizado')
        pending['commitments'] = opened.count()
        pending['overdue'] = opened.filter(fecha_comprometida__lt=today).count()
        for obj in opened.order_by('fecha_comprometida', 'pk')[:5]:
            priority = 'overdue' if obj.fecha_comprometida < today else 'soon' if obj.fecha_comprometida <= today+timedelta(days=7) else 'normal'
            tasks.append(task('commitment', obj, obj.descripcion, f'pages/compromiso-detalle.html?id={obj.pk}', priority, obj.fecha_comprometida))
    corrective = None
    if evidence is not None:
        pending['waiting'] = evidence.filter(estado='Pendiente').count()
        if allowed('actividades', 'editar'):
            corrective = evidence.filter(estado__in=['Corrección', 'Rechazada'])
            pending['correction'] = corrective.count()
            for obj in corrective.only('id', 'nombre_archivo')[:5]:
                tasks.append(task('correction', obj, obj.nombre_archivo, f'pages/evidencias.html?registro={obj.pk}', 'action'))
    if activities is not None and allowed('actividades', 'editar'):
        drafts = activities.filter(estado='Borrador')
        pending['drafts'] = drafts.count()
        for obj in drafts.only('id', 'solicitud')[:3]:
            tasks.append(task('draft', obj, obj.solicitud, f'pages/desempeno.html?registro={obj.pk}', 'normal'))
        corrections = activities.filter(estado__in=['Corrección', 'Rechazada'])
        if corrective is not None:
            corrections = corrections.exclude(pk__in=corrective.values('actividad_id'))
        pending['activity_correction'] = corrections.count()
        for obj in corrections.only('id', 'solicitud')[:3]:
            tasks.append(task('activity_correction', obj, obj.solicitud, f'pages/desempeno.html?registro={obj.pk}', 'action'))
    if allowed('evidencias') and allowed('evidencias', 'revisar'):
        reviews = domain.scoped(request, 'evidencias').filter(estado='Pendiente', siguiente_version__isnull=True).exclude(Q(autor=user) | Q(actividad__autor=user))
        pending['review'] = reviews.count()
        for obj in reviews.order_by('creado', 'pk').only('id', 'nombre_archivo')[:5]:
            tasks.append(task('review', obj, obj.nombre_archivo, f'pages/validacion.html?registro={obj.pk}', 'action'))
    ranking = {'overdue': 0, 'action': 1, 'soon': 2, 'normal': 3}
    tasks.sort(key=lambda t: (ranking[t['priority']], t['due'] or '', t['id']))
    response = api.ok(dict(period=period, generated_at=timezone.now().isoformat(),
                           delegation=delegation.nombre, month=month_data, weeks=weeks,
                           pending=pending, tasks=tasks[:12],
                           scope='Solo tus registros en la delegación activa. Pendientes de todo el historial; avance del mes seleccionado.'))
    response['Cache-Control'] = 'private, no-store'
    return response
