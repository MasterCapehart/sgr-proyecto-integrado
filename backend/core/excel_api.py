"""Seguimiento de derivaciones y expedientes sociales del contexto autorizado."""
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count, Max
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from . import local_api as api
from . import domain_api as domain
from .models import Actividad, DerivacionActividad, Atencion

@require_http_methods(['POST'])
def derivation(request,pk):
    denied=domain.gate(request,'actividades','editar')
    if denied:return denied
    try:
        data=api.body(request)
        if set(data)-{'_version','destino','motivo','estado'}:return api.error('Campos de derivación no permitidos.')
        with transaction.atomic():
            obj=domain.scoped(request,'actividades').select_for_update().filter(pk=pk).first()
            if not obj:return api.error('Actividad no encontrada.',404)
            if obj.autor_id!=request.user.pk and not api.allowed(request.user,'actividades','editar_equipo'):return api.error('No puedes derivar una actividad ajena.',403)
            closed=domain.check_closed_quarter(obj.fecha)
            if closed:return api.error(f'El trimestre {closed.nombre} está cerrado. Se requiere una reapertura autorizada para derivar actividades.',400)
            if obj.estado in ['Validada','Aprobada y pondera','Aprobada y no pondera']:
                return api.error('Las actividades aprobadas están protegidas y no admiten modificaciones ni derivación.',400)
            if obj.estado=='Anulada':
                return api.error('Las actividades anuladas están protegidas y no admiten derivación.',400)
            conflict=domain.validate_version(obj,data)
            if conflict:return conflict
            for key,limit in [('destino',200),('motivo',2000)]:
                if not isinstance(data.get(key),str) or not data[key].strip() or len(data[key])>limit:return api.error(f'{key}: texto obligatorio de hasta {limit} caracteres.')
            if data.get('estado') not in ['Pendiente','En proceso','Resuelta']:return api.error('Estado de derivación inválido.')
            previous=domain.representation(obj)
            event=DerivacionActividad(actividad=obj,autor=request.user,destino=data['destino'].strip(),motivo=data['motivo'].strip(),estado=data['estado']);event.full_clean();event.save()
            obj.derivado_a=event.destino;obj.estado_derivacion=event.estado;obj.version+=1;obj.save(update_fields=['derivado_a','estado_derivacion','version'])
            api.record_event(request,'actividades',obj.pk,'derivar',previous,domain.representation(obj))
        return api.ok(domain.representation(obj))
    except (ValidationError,ValueError,TypeError):return api.error('Datos de derivación inválidos.')

@require_http_methods(['GET'])
def cases(request,code=None):
    denied=domain.gate(request,'atenciones','ver')
    if denied:return denied
    d=api.active_delegation(request)
    qs=Atencion.objects.filter(Q(delegacion=d)|Q(delegacion_responsable=d)).exclude(caso_social__isnull=True).exclude(caso_social='')
    if code:
        records=qs.filter(caso_social=code.upper()).order_by('numero_gestion','id')
        first=records.first()
        if first is None:return api.error('Expediente no encontrado.',404)
        return api.ok({'codigo':first.caso_social,'solicitante':first.solicitante,'rut_solicitante':records.exclude(rut_solicitante='').values_list('rut_solicitante',flat=True).first() or '', 'telefono_solicitante':records.exclude(telefono_solicitante='').values_list('telefono_solicitante',flat=True).last() or '','gestiones':[api.serialize(o,api.RESOURCES['atenciones'][1]) for o in records]})
    search=request.GET.get('search','').strip()
    if search:
        codes=qs.filter(Q(caso_social__icontains=search)|Q(solicitante__icontains=search)|Q(rut_solicitante__icontains=search)).values('caso_social')
        qs=qs.filter(caso_social__in=codes)
    if request.GET.get('export')=='1':return social_export(request,qs)
    grouped=qs.values('caso_social').annotate(solicitante=Max('solicitante'),total_gestiones=Count('id'),ultima_fecha=Max('fecha_registro')).order_by('-ultima_fecha','caso_social')
    try:page=int(request.GET.get('page',1))
    except (ValueError,TypeError):return api.error('Página inválida.')
    pager=Paginator(grouped,20)
    if page<1 or page>pager.num_pages:return api.error('Página inexistente.',404)
    results=[]
    for row in pager.page(page):
        row.update(case_summary(qs.filter(caso_social=row['caso_social']).order_by('numero_gestion','id')));results.append(row)
    return api.ok(results=results,count=pager.count,page=page,total_pages=pager.num_pages,columnas=SOCIAL_COLUMNS)

def diff_days(d1, d2):
    if not d1 or not d2:return None
    try:
        from datetime import date, datetime
        if isinstance(d1, datetime): d1 = d1.date()
        elif isinstance(d1, str): d1 = date.fromisoformat(str(d1)[:10])
        if isinstance(d2, datetime): d2 = d2.date()
        elif isinstance(d2, str): d2 = date.fromisoformat(str(d2)[:10])
        days = (d2 - d1).days
        if days < 0:
            return None
        return days
    except Exception:return None

SOCIAL_COLUMNS=[('caso_social','Código caso'),('fecha_ingreso','Fecha ingreso'),('tipo_nombre','Tipo atención'),('subatencion_nombre','Sub atención'),('solicitante','Usuario / vecino'),('rut','RUT'),('telefono','Teléfono'),('requiere_visita','Requiere visita'),('compromiso','Ingreso al tubo'),('primera','Primera gestión'),('programada','Fecha programada visita'),('observaciones','Observaciones'),('segunda','Segunda gestión'),('realizada','Fecha visita realizada'),('informe','Fecha entrega informe'),('tercera','Tercera gestión'),('beneficio','Fecha entrega beneficio'),('tiempo_ingreso_primera','Días ingreso-primera'),('tiempo_programacion_visita','Días prog-visita'),('tiempo_visita_informe','Días visita-informe'),('tiempo_atencion_beneficio','Días atenc-beneficio'),('fecha_atencion','Fecha atención'),('estado_general','Estado general'),('fecha_cierre','Fecha cierre'),('resultado','Resultado del caso')]
def case_summary(records):
    rows=list(records);first=rows[0]
    def latest(name):return next((getattr(r,name) for r in reversed(rows) if getattr(r,name) not in ['',None]),None)
    from .local_api import serialize,RESOURCES
    initial=serialize(first,RESOURCES['atenciones'][1])
    g1 = next((r for r in rows if r.numero_gestion==1), first)
    g1_fecha = g1.fecha_visita_realizada or g1.fecha_visita or timezone.localtime(g1.fecha_registro).date()
    fecha_atencion_str = g1_fecha.isoformat() if hasattr(g1_fecha, 'isoformat') else str(g1_fecha)
    beneficio = latest('fecha_entrega_beneficio')
    informe = latest('fecha_entrega_informe')
    realizada = latest('fecha_visita_realizada')
    cierre_keywords = ['cierre', 'concluido', 'finalizado', 'terminado', 'no procede', 'rechazado', 'desistido', 'sin beneficio']
    is_closed_by_gestion = any(any(kw in (r.tipo_gestion or '').lower() or kw in (r.gestion_realizada or '').lower() for kw in cierre_keywords) for r in rows)

    if beneficio:
        estado_general = 'Cerrado'
        resultado = 'Beneficio entregado'
        fecha_cierre = beneficio
    elif is_closed_by_gestion:
        estado_general = 'Cerrado'
        closing_r = next((r for r in reversed(rows) if any(kw in (r.tipo_gestion or '').lower() or kw in (r.gestion_realizada or '').lower() for kw in cierre_keywords)), rows[-1])
        resultado = closing_r.tipo_gestion if (closing_r.tipo_gestion and any(kw in closing_r.tipo_gestion.lower() for kw in cierre_keywords)) else (closing_r.gestion_realizada or 'Caso social cerrado')
        closing_date = closing_r.fecha_entrega_informe or closing_r.fecha_visita_realizada or timezone.localtime(closing_r.fecha_registro).date()
        fecha_cierre = closing_date.isoformat() if hasattr(closing_date, 'isoformat') else str(closing_date)
    elif informe or realizada:
        estado_general = 'En seguimiento'
        resultado = 'Informe emitido' if informe else 'Visita realizada'
        fecha_cierre = None
    elif rows:
        estado_general = 'En atención inicial'
        resultado = 'En evaluación social'
        fecha_cierre = None
    else:
        estado_general = 'Pendiente'
        resultado = 'Sin iniciar'
        fecha_cierre = None
    derivs = []
    for r in rows:
        for d in getattr(r, 'derivaciones_auditadas', []).all():
            dest = getattr(d, 'delegacion_destino', None)
            if dest: derivs.append(dest.nombre)
    result={'caso_social':first.caso_social,'fecha_ingreso':timezone.localtime(first.fecha_registro).date().isoformat(),'fecha_atencion':fecha_atencion_str,'estado_general':estado_general,'fecha_cierre':fecha_cierre,'resultado':resultado,'derivaciones':derivs,'tipo_nombre':initial['tipo_nombre'],'subatencion_nombre':initial['subatencion_nombre'],'solicitante':first.solicitante,'rut':latest('rut_solicitante') or '', 'telefono':latest('telefono_solicitante') or '', 'requiere_visita':'No informado' if latest('requiere_visita') is None else 'Sí' if latest('requiere_visita') else 'No','compromiso':latest('compromiso_id') or '', 'programada':latest('fecha_visita_programada'),'realizada':realizada,'informe':informe,'beneficio':beneficio,'observaciones':latest('gestion_realizada') or first.descripcion}
    for number,key in [(1,'primera'),(2,'segunda'),(3,'tercera')]:
        row=next((r for r in rows if r.numero_gestion==number),None);result[key]=(row.tipo_gestion or 'Registrada sin tipo especificado') if row else 'Sin registrar'
    t1 = diff_days(result['fecha_ingreso'], g1_fecha)
    t2 = diff_days(result['programada'], result['realizada'] or latest('fecha_visita'))
    t3 = diff_days(result['realizada'] or latest('fecha_visita'), result['informe'])
    t4_ingreso = diff_days(result['fecha_ingreso'], result['beneficio'])
    t4_atencion = diff_days(result['fecha_atencion'], result['beneficio'])
    result['tiempo_ingreso_primera'] = t1 if t1 is not None else 'No calculable'
    result['tiempo_programacion_visita'] = t2 if t2 is not None else 'No calculable'
    result['tiempo_visita_informe'] = t3 if t3 is not None else 'No calculable'
    result['tiempo_atencion_beneficio'] = t4_atencion if t4_atencion is not None else (t4_ingreso if t4_ingreso is not None else 'No calculable')
    result['tiempos'] = {
        'ingreso_primera': t1,
        'programacion_visita': t2,
        'visita_informe': t3,
        'atencion_beneficio': t4_atencion,
        'ingreso_beneficio': t4_ingreso,
    }
    return result

def social_export(request,qs):
    from io import BytesIO
    from django.http import HttpResponse
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill
    if not api.allowed(request.user,'atenciones','exportar'):return api.error('No tienes permiso para exportar atenciones.',403)
    book=Workbook();sheet=book.active;sheet.title='Gestión social';sheet.append([label for key,label in SOCIAL_COLUMNS]);codes=list(qs.order_by('caso_social').values_list('caso_social',flat=True).distinct())
    for code in codes:
        row=case_summary(qs.filter(caso_social=code).order_by('numero_gestion','id'));sheet.append([row[key] for key,label in SOCIAL_COLUMNS])
        for cell in sheet[sheet.max_row]:
            if isinstance(cell.value,str):cell.data_type='s'
    for cell in sheet[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='AD0000')
    for col in sheet.columns:sheet.column_dimensions[col[0].column_letter].width=27
    sheet.freeze_panes='F2';sheet.auto_filter.ref=sheet.dimensions;out=BytesIO();book.save(out);response=HttpResponse(out.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');response['Content-Disposition']='attachment; filename="gestion-social.xlsx"';api.record_event(request,'atenciones',None,'exportar_social',None,{'casos':len(codes)});return response
