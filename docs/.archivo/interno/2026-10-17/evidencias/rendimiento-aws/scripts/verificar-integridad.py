import json
from pathlib import Path
from django.db.models import Count
from core.models import Atencion,Usuario
cfg=json.loads(Path('/home/ubuntu/ren-private.json').read_text());tag=cfg['tag'];confirmed=json.loads(Path('/home/ubuntu/claves-confirmadas.json').read_text());q=Atencion.objects.filter(clave_idempotencia__startswith=tag+'-vu');actual=dict(q.values_list('clave_idempotencia','id'));missing=[k for k,v in confirmed.items() if actual.get(k)!=v]
wrong=[x for x in q.values('clave_idempotencia','usuario_id','delegacion_id') if x['delegacion_id']!=cfg['delegacion'] or x['usuario_id']!=cfg['accounts'][int(x['clave_idempotencia'].split('-vu')[1].split('-')[0])]['id']]
report={'tag':tag,'semillas_d01':Atencion.objects.filter(clave_idempotencia__startswith=tag+'-seed-',delegacion_id=cfg['delegacion']).count(),'semillas_d02':Atencion.objects.filter(clave_idempotencia__startswith=tag+'-seed-',delegacion_id=cfg['delegacion_ajena']).count(),'escrituras_db':len(actual),'confirmadas_cliente':len(confirmed),'confirmadas_ausentes_o_id_distinto':len(missing),'escrituras_sin_confirmacion_cliente':len(set(actual)-set(confirmed)),'duplicados_clave':list(q.values('clave_idempotencia').annotate(n=Count('id')).filter(n__gt=1)),'autor_o_delegacion_incorrectos':len(wrong)}
report['integridad_confirmada']=report['semillas_d01']==10000 and report['semillas_d02']==100 and not missing and not wrong and not report['duplicados_clave']
p=Path('/home/ubuntu/integridad-resultado.json');p.write_text(json.dumps(report,indent=2));p.chmod(0o644);print(json.dumps(report))
