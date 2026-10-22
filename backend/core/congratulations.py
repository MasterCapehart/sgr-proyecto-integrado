"""R11: registro y revisión explícita por delegado. Nunca concede puntos."""
from .models import RevisionFelicitacion

def manager(user):
    return bool(user.is_authenticated and user.is_active and user.rol_id and user.rol.estado and user.rol.nombre.strip().casefold()=='delegado')

def conditions(obj,backing):
    reasons=[]
    if not obj.vecino.strip():reasons.append('Falta identificar al vecino o usuario emisor.')
    if obj.procedencia!='Directa':reasons.append('Debe provenir directamente del vecino o usuario; un mensaje personal requiere formalización.')
    if obj.destinatario not in ['Delegado','Delegación']:reasons.append('Debe estar dirigida al delegado o a la delegación.')
    if not backing:reasons.append('Falta adjuntar un respaldo formal verificable.')
    return reasons

def backing_data(b):
    return dict(id=b.pk,nombre=b.nombre,tipo_mime=b.tipo_mime,tamano=b.tamano,sha256=b.sha256,autor=b.autor_id,creado=b.creado.isoformat(),archivo_url=f'/api/reclamos/{b.reclamo_id}/respaldos/{b.pk}/archivo/')

def review_data(r):
    return dict(id=r.pk,version_registro=r.version_registro,decision=r.decision,observacion=r.observacion,respaldo=r.respaldo_id,autor=r.autor_id,autor_nombre=r.autor.get_full_name() or r.autor.username,creado=r.creado.isoformat(),snapshot=r.snapshot)

def describe(obj):
    if obj.clase!='Felicitación':return dict(revision=dict(estado='No aplica',potencialmente_puntuable=False,motivos=[]),respaldos=[],revisiones=[])
    backups=list(obj.respaldos_formales.all());reviews=list(obj.revisiones_formales.select_related('autor'))
    last=reviews[0] if reviews else None
    state=last.decision if last and last.version_registro==obj.version else 'Pendiente'
    reasons=conditions(obj,backups[0] if backups else None)
    if state=='Pendiente':reasons.append('Pendiente de revisión explícita del delegado.')
    if state=='Rechazada':reasons.append('Rechazada por el delegado: '+last.observacion)
    return dict(revision=dict(estado=state,potencialmente_puntuable=state=='Validada' and not reasons,motivos=reasons,
        alcance='Validación formal preliminar: no concede puntos ni calcula metas.'),respaldos=[backing_data(b) for b in backups],revisiones=[review_data(r) for r in reviews])
