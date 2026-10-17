"""Propuesta explícita y editable de transiciones; su aceptación no se simula."""
from .models import PoliticaOperativa, Rol
STATES=['Ingresado','Pendiente','En proceso','Realizado']
PROPOSAL={'Ingresado':['Pendiente','En proceso','Realizado'],'Pendiente':['En proceso','Realizado'],'En proceso':['Pendiente','Realizado'],'Realizado':[]}

def current():
    row=PoliticaOperativa.objects.order_by('-version').first()
    return {'version':row.version if row else 0,'transiciones':row.transiciones if row else PROPOSAL,'validada':bool(row and row.validada and row.permisos_snapshot==permissions_snapshot()),'alcance':'Pruebas locales','motivo':row.motivo if row else 'Propuesta local pendiente de validación funcional','fecha':row.fecha.isoformat() if row else None,'autor':row.autor.username if row else None}

def permissions_snapshot():
    return [{'id':r.pk,'version':r.version,'nombre':r.nombre,'alcance':r.alcance,'estado':r.estado,'permisos':sorted(r.permisos)} for r in Rol.objects.order_by('id')]
