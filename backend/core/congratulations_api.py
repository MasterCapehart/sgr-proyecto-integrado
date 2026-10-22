"""Respaldos privados y revisiones inmutables de felicitaciones."""
import hashlib,uuid
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import FileResponse
from django.views.decorators.http import require_http_methods
from . import local_api as api,domain_api as domain,congratulations as service
from .models import RespaldoFelicitacion,RevisionFelicitacion

# Imports inside handlers avoid coupling serialization back to this module.
def gate(request,write=False):
    denied=domain.gate(request,'reclamos','editar' if write else 'ver')
    if denied:return denied
    if write and not service.manager(request.user):return api.error('Solo el delegado puede gestionar y validar felicitaciones.',403)

def authorized(request,pk):
    from .feedback_api import scoped
    return scoped(request).select_for_update().filter(pk=pk,clase='Felicitación').first()

def conflict(request,obj,values):
    if obj.autor_id!=request.user.pk and not api.allowed(request.user,'reclamos','editar_equipo'):return api.error('No puedes editar un registro ajeno.',403)
    return domain.validate_version(obj,values)

def failure(ex):
    if isinstance(ex,ValidationError):return api.error('; '.join(ex.messages))
    from .storage_errors import storage_error
    result=storage_error(ex)
    if result:return api.error(result[1],result[0])
    raise ex

@require_http_methods(['POST'])
def upload(request,pk):
    denied=gate(request,True)
    if denied:return denied
    saved=None
    try:
        if set(request.POST)-{'_version'} or set(request.FILES)!={'archivo'}:raise ValidationError('Adjunta un archivo y la versión del registro.')
        file=request.FILES.get('archivo')
        if not file or not 0<file.size<=10*1024*1024:raise ValidationError('Adjunta un archivo de hasta 10 MB.')
        signature=file.read(12);file.seek(0);ext=Path(file.name).suffix.lower()
        mime='application/pdf' if ext=='.pdf' and signature.startswith(b'%PDF-') else 'image/png' if ext=='.png' and signature.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if ext in ['.jpg','.jpeg'] and signature.startswith(b'\xff\xd8\xff') else None
        if not mime:raise ValidationError('Solo se admiten PDF, PNG y JPEG con contenido compatible.')
        version=request.POST.get('_version','')
        if not version.isdigit():raise ValidationError('Falta la versión del registro.')
        digest=hashlib.sha256()
        for chunk in file.chunks():digest.update(chunk)
        file.seek(0)
        from .feedback_api import data
        with transaction.atomic():
            obj=authorized(request,pk)
            if not obj:return api.error('Felicitación no encontrada.',404)
            denied=conflict(request,obj,{'_version':int(version)})
            if denied:return denied
            before=data(obj)
            b=RespaldoFelicitacion(reclamo=obj,autor=request.user,nombre=Path(file.name).name[:255],tipo_mime=mime,tamano=file.size,sha256=digest.hexdigest())
            b.archivo.save(uuid.uuid4().hex+ext,file,save=False);saved=b.archivo;b.full_clean();b.save()
            obj.version+=1;obj.save(update_fields=['version'])
            api.record_event(request,'reclamos',obj.pk,'adjuntar_respaldo',before,data(obj))
        response=api.ok(data(obj));response.status_code=201;return response
    except Exception as ex:
        if saved:saved.delete(save=False)
        return failure(ex)

@require_http_methods(['POST'])
def review(request,pk):
    denied=gate(request,True)
    if denied:return denied
    try:
        incoming=api.body(request)
        if set(incoming)!={'_version','decision','observacion'}:raise ValidationError('Indica versión, decisión y observación.')
        decision=incoming['decision'];note=incoming['observacion']
        if decision not in ['Validada','Rechazada']:raise ValidationError('Decisión inválida.')
        if not isinstance(note,str) or not note.strip() or len(note)>2000:raise ValidationError('Indica una observación de hasta 2000 caracteres.')
        from .feedback_api import data
        with transaction.atomic():
            obj=authorized(request,pk)
            if not obj:return api.error('Felicitación no encontrada.',404)
            denied=conflict(request,obj,incoming)
            if denied:return denied
            before=data(obj);b=obj.respaldos_formales.first()
            if decision=='Validada':
                reasons=service.conditions(obj,b)
                if reasons:raise ValidationError(reasons)
                if not b.archivo.storage.exists(b.archivo.name):raise ValidationError('El respaldo no está disponible; adjunta un respaldo verificable.')
            obj.version+=1;obj.save(update_fields=['version'])
            RevisionFelicitacion.objects.create(reclamo=obj,version_registro=obj.version,decision=decision,observacion=note.strip(),respaldo=b,autor=request.user,
                snapshot=dict(fecha=str(obj.fecha),emisor=obj.vecino,contacto=obj.contacto,procedencia=obj.procedencia,destinatario=obj.destinatario,situacion=obj.situacion,profesional=obj.profesional_id,respaldo_sha256=b.sha256 if b else None))
            api.record_event(request,'reclamos',obj.pk,'validar_felicitacion' if decision=='Validada' else 'rechazar_felicitacion',before,data(obj))
        return api.ok(data(obj))
    except Exception as ex:return failure(ex)

@require_http_methods(['GET'])
def download(request,pk,backing):
    denied=gate(request)
    if denied:return denied
    from .feedback_api import scoped
    obj=scoped(request).filter(pk=pk,clase='Felicitación').first()
    b=obj.respaldos_formales.filter(pk=backing).first() if obj else None
    if not b:return api.error('Archivo no encontrado.',404)
    try:r=FileResponse(b.archivo.open('rb'),as_attachment=True,filename=b.nombre,content_type=b.tipo_mime)
    except Exception as ex:return failure(ex)
    r['X-Content-Type-Options']='nosniff';r['Cache-Control']='private, no-store';return r
