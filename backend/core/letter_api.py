"""Cartas compartidas por delegación, edición responsable y archivos fuera de MEDIA_URL."""
import re
from pathlib import Path
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction,IntegrityError
from django.db.models import Q
from django.http import FileResponse
from django.views.decorators.http import require_http_methods
from . import local_api as api,domain_api as domain
from .capture_followup import fingerprint
from .letter_models import Carta,DocumentoCarta,STATES,TRANSITIONS,validate_transition
from .models import Usuario,EventoLocal
FIELDS=('numero_carta','fecha','remitente','destinatario','telefono','materia','fecha_respuesta','responsable','area_derivada','pronunciamiento','observaciones')
def manager(u):return u.is_superuser or bool(u.rol_id and u.rol.estado and u.rol.nombre.strip().casefold() in ['administrador','delegado'])
def elevated(u,action='gestionar'):return manager(u) and api.allowed(u,'cartas',action)
def editable(u,c):return c.responsable_id==u.pk or elevated(u)
def scope(request):return Carta.objects.filter(delegacion=api.active_delegation(request)).select_related('responsable')
def people(request):
    d=api.active_delegation(request)
    return Usuario.objects.filter(is_active=True).filter(Q(delegacion=d)|Q(delegaciones=d)).distinct()
def document_data(d):return dict(id=d.pk,nombre=d.nombre,tamano=d.tamano,url=f'/api/cartas/{d.carta_id}/documentos/{d.pk}/')
def serialize(c,detail=False,user=None):
    r=dict(id=c.pk,codigo=c.codigo,estado=c.estado,version=c.version,delegacion=c.delegacion_id,fecha_cierre=str(c.fecha_cierre) if c.fecha_cierre else None,responsable_nombre=c.responsable.get_full_name() or c.responsable.username,**{f:(c.responsable_id if f=='responsable' else getattr(c,f)) for f in FIELDS})
    for key in ['fecha','fecha_respuesta']:
        if r[key] is not None:r[key]=str(r[key])
    if user:r.update(puede_editar=editable(user,c) and c.estado not in ['Finalizada','No aplica'],puede_reabrir=elevated(user,'reabrir') and c.estado in ['Finalizada','No aplica'])
    if detail:
        r['documentos']=[document_data(d) for d in c.documentos.all()]
        r['historial']=[dict(fecha=e.fecha,autor=e.usuario_id,accion=e.accion,datos=e.despues) for e in EventoLocal.objects.filter(recurso='cartas',registro=c.pk).order_by('-pk')[:100]]
    return r
def response(data=None,**extra):
    r=api.ok(data,**extra);r['Cache-Control']='private, no-store';return r
def fail(ex):return api.error('; '.join(ex.messages) if isinstance(ex,ValidationError) else 'Datos inválidos.')
def version(c,data):
    if isinstance(data.get('_version'),bool) or data.pop('_version',None)!=c.version:raise ValidationError('El registro cambió. Recarga antes de guardar.')
def apply(c,data,request):
    if set(data)-set(FIELDS):raise ValidationError('Hay campos no editables.')
    for f,v in data.items():
        if f=='responsable':
            if isinstance(v,bool) or not str(v).isdigit():raise ValidationError('Responsable inválido.')
            if int(v)!=c.responsable_id and not elevated(request.user,'reasignar'):raise ValidationError('No tienes permiso para asignar a otro responsable.')
            u=people(request).filter(pk=v).first()
            if not u:raise ValidationError('Responsable fuera de la delegación activa.')
            c.responsable=u
        elif f in ['fecha','fecha_respuesta']:setattr(c,f,v or None)
        else:
            if not isinstance(v,str):raise ValidationError('Los campos deben contener texto.')
            setattr(c,f,v.strip())
    if c.telefono and not re.fullmatch(r'\+?[0-9 ()-]{8,30}',c.telefono):raise ValidationError('Teléfono inválido.')
    c.full_clean()
def replay(request,key,digest):
    c=Carta.objects.filter(clave_idempotencia=key).first()
    if c:
        if c.delegacion_id!=api.active_delegation(request).pk or c.creado_por_id!=request.user.pk or c.captura_hash!=digest:return api.error('Clave de registro utilizada con otros datos.',409)
        return response(serialize(c,user=request.user),is_duplicate_prevented=True)
@require_http_methods(['GET'])
def options(request):
    denied=domain.gate(request,'cartas','ver')
    if denied:return denied
    return response(estados=STATES,transiciones=TRANSITIONS,responsables=[dict(id=u.pk,nombre=u.get_full_name() or u.username) for u in people(request)],puede_asignar=elevated(request.user,'reasignar'))
@require_http_methods(['GET','POST','PATCH'])
def records(request,pk=None,action=None):
    permission='reabrir' if action=='reabrir' else 'ver' if request.method=='GET' else 'crear' if not pk else 'editar'
    denied=domain.gate(request,'cartas',permission)
    if denied:return denied
    if action and request.method!='POST' or not pk and request.method=='PATCH' or pk and request.method=='POST' and not action:return api.error('Método no permitido.',405)
    try:
        if request.method=='GET':
            if pk:
                c=scope(request).filter(pk=pk).first()
                return response(serialize(c,True,request.user)) if c else api.error('Carta no encontrada.',404)
            qs=scope(request);q=request.GET.get('q','').strip()[:150]
            if q:qs=qs.filter(Q(codigo__icontains=q)|Q(numero_carta__icontains=q)|Q(remitente__icontains=q)|Q(destinatario__icontains=q)|Q(materia__icontains=q))
            for f in ['estado','responsable']:
                if request.GET.get(f):qs=qs.filter(**{f:request.GET[f]})
            for param,lookup in [('desde','fecha__gte'),('hasta','fecha__lte')]:
                if request.GET.get(param):qs=qs.filter(**{lookup:request.GET[param]})
            order=request.GET.get('orden','-fecha');qs=qs.order_by(order if order in ['fecha','-fecha','numero_carta','estado'] else '-fecha','-pk')
            p=Paginator(qs,20).get_page(request.GET.get('page'));return response(results=[serialize(c,user=request.user) for c in p],count=p.paginator.count,page=p.number,total_pages=p.paginator.num_pages)
        data=api.body(request)
        with transaction.atomic():
            c=scope(request).select_for_update().filter(pk=pk).first() if pk else None
            if pk and not c:return api.error('Carta no encontrada.',404)
            before=serialize(c) if c else None
            if c:
                if not editable(request.user,c):return api.error('Solo el responsable o gestor autorizado puede modificar esta carta.',403)
                if isinstance(data.get('_version'),bool) or data.get('_version')!=c.version:return api.error('La carta cambió. Recarga antes de guardar.',409)
                data.pop('_version')
                if action=='reabrir':
                    if not elevated(request.user,'reabrir'):return api.error('Reapertura reservada a administrador o delegado autorizado.',403)
                    if c.estado not in ['Finalizada','No aplica'] or set(data)!={'motivo'} or not isinstance(data['motivo'],str) or not data['motivo'].strip():raise ValidationError('Reabrir requiere estado terminal y motivo.')
                    c.estado='En proceso';c.fecha_cierre=None
                else:
                    if c.estado in ['Finalizada','No aplica']:raise ValidationError('La carta está cerrada. Requiere reapertura autorizada.')
                    if action=='estado':
                        if set(data)-{'estado','pronunciamiento','fecha_cierre','observaciones','area_derivada'}:raise ValidationError('Campos de transición inválidos.')
                        validate_transition(c.estado,data.get('estado'));c.estado=data.pop('estado')
                        c.fecha_cierre=data.pop('fecha_cierre',None) or None
                    apply(c,data,request)
                c.full_clean();c.version+=1
            else:
                key=data.pop('clave_idempotencia',None)
                if not isinstance(key,str) or not key.strip() or len(key)>64:raise ValidationError('Falta clave idempotente de registro.')
                digest=fingerprint(data);prior=replay(request,key,digest)
                if prior:return prior
                c=Carta(delegacion=api.active_delegation(request),responsable=request.user,creado_por=request.user,clave_idempotencia=key,captura_hash=digest);apply(c,data,request)
            c.save();after=serialize(c)
            if action=='reabrir':after['motivo']=data['motivo'].strip()
            api.record_event(request,'cartas',c.pk,action or ('editar' if pk else 'crear'),before,after)
            r=response(serialize(c,True,request.user));r.status_code=200 if pk else 201;return r
    except IntegrityError:
        if 'key' in locals():
            prior=replay(request,key,digest)
            if prior:return prior
        return api.error('Registro simultáneo. Recarga antes de continuar.',409)
    except (ValidationError,ValueError,TypeError) as ex:
        if 'key' in locals() and 'digest' in locals():
            prior=replay(request,key,digest)
            if prior:return prior
        return fail(ex)

def inspect_file(f):
    if not f or f.size>10*1024*1024 or f.size==0:raise ValidationError('Selecciona un documento de hasta 10 MB.')
    prefix=f.read(16);f.seek(0)
    ext=Path(f.name).suffix.lower()
    mime='application/pdf' if prefix.startswith(b'%PDF-') and ext=='.pdf' else 'image/png' if prefix.startswith(b'\x89PNG\r\n\x1a\n') and ext=='.png' else 'image/jpeg' if prefix.startswith(b'\xff\xd8\xff') and ext in ['.jpg','.jpeg'] else None
    if not mime:raise ValidationError('El documento debe ser PDF, PNG o JPEG con contenido válido.')
    if mime=='application/pdf':
        f.seek(max(0,f.size-1024));tail=f.read();f.seek(0)
        if b'%%EOF' not in tail:raise ValidationError('PDF incompleto o inválido.')
        from pypdf import PdfReader
        try:
            pdf=PdfReader(f,strict=True)
            if pdf.is_encrypted or not len(pdf.pages):raise ValueError('PDF vacío o cifrado')
        except Exception:raise ValidationError('PDF inválido, vacío o cifrado.')
        finally:f.seek(0)
    if mime.startswith('image/'):
        from PIL import Image
        try:Image.open(f).verify()
        except Exception:raise ValidationError('Imagen inválida.')
        finally:f.seek(0)
    return mime
@require_http_methods(['GET','POST'])
def documents(request,pk,document_id=None):
    denied=domain.gate(request,'cartas','ver' if request.method=='GET' else 'editar')
    if denied:return denied
    stored=None
    try:
        with transaction.atomic():
            c=scope(request).select_for_update().filter(pk=pk).first()
            if not c:return api.error('Carta no encontrada.',404)
            if request.method=='GET':
                d=c.documentos.filter(pk=document_id).first()
                if not d:return api.error('Documento no encontrado.',404)
                handle=d.archivo.open('rb');api.record_event(request,'cartas',c.pk,'descargar_documento',None,{'documento':d.pk})
                r=FileResponse(handle,as_attachment=True,filename=d.nombre,content_type=d.mime);r['Cache-Control']='private, no-store';r['X-Content-Type-Options']='nosniff';return r
            if document_id:return api.error('Método no permitido.',405)
            if not editable(request.user,c):return api.error('No tienes permiso para adjuntar documentos.',403)
            if c.estado in ['Finalizada','No aplica']:raise ValidationError('Reabre la carta antes de adjuntar documentos.')
            data=api.body(request)
            if str(c.version)!=data.get('_version'):return api.error('La carta cambió. Recarga antes de adjuntar.',409)
            if set(data)-{'_version'} or set(request.FILES)!={'archivo'}:raise ValidationError('Adjunta un único archivo.')
            f=request.FILES['archivo'];mime=inspect_file(f)
            d=DocumentoCarta(carta=c,autor=request.user,nombre=Path(f.name).name[:200],tamano=f.size,mime=mime)
            d.archivo.save(f.name,f,save=False);stored=d.archivo;d.save();c.version+=1;c.save()
            api.record_event(request,'cartas',c.pk,'adjuntar_documento',None,dict(documento=d.pk,nombre=d.nombre,version=c.version))
            return response(serialize(c,True,request.user))
    except (ValidationError,ValueError,TypeError) as ex:
        if stored:stored.delete(save=False)
        return fail(ex)
    except (FileNotFoundError,OSError):
        if stored:stored.delete(save=False)
        return api.error('El documento no está disponible. Intenta nuevamente o contacta al administrador.',503)
    except Exception:
        if stored:stored.delete(save=False)
        raise
