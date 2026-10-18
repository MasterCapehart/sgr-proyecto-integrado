from pathlib import Path
import json
from core.models import Usuario,Rol
from django.db import transaction
x=json.loads(Path('/home/ubuntu/cleanup-tags.json').read_text());result=[]
with transaction.atomic():
 for tag in x['tags']:
  assert tag.startswith(('REN','Q')) and len(tag)>=9
  users=Usuario.objects.filter(username__startswith=tag.lower(),email__endswith='@example.test',is_superuser=False)
  ids=list(users.values_list('id',flat=True));before=users.filter(is_active=True).count();users.update(is_active=False)
  roles=Rol.objects.filter(nombre__startswith=tag)
  for role in roles:
   if not Usuario.objects.filter(rol=role,is_active=True).exists():role.estado=False;role.save(update_fields=['estado'])
  result.append({'tag':tag,'cuentas_ficticias':len(ids),'activas_antes':before,'activas_despues':users.filter(is_active=True).count()})
p=Path('/home/ubuntu/cleanup-resultado.json');p.write_text(json.dumps(result,indent=2));p.chmod(0o644);print(json.dumps(result))
