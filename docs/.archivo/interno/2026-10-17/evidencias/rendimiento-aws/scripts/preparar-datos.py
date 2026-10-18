import os,json,secrets,uuid
from pathlib import Path
from django.contrib.auth.hashers import make_password
from core.models import Delegacion,Rol,Usuario,TipoAtencion,SubAtencion,Atencion
from django.db import transaction
TAG='REN'+uuid.uuid4().hex[:8]
with transaction.atomic():
 d=Delegacion.objects.create(codigo=TAG+'A',nombre=TAG+' QA D01 ficticia')
 d2=Delegacion.objects.create(codigo=TAG+'B',nombre=TAG+' QA D02 ficticia')
 role=Rol.objects.create(nombre=TAG+' Operador QA',permisos=['atenciones.ver','atenciones.crear','atenciones.exportar','indicadores.ver'],alcance='delegacion')
 t=TipoAtencion.objects.create(codigo=TAG,nombre=TAG+' Tipo QA ficticio')
 s=SubAtencion.objects.create(codigo=TAG,nombre=TAG+' Sub QA ficticia',tipo_atencion=t)
 accounts=[]
 for n in range(51):
  pw=secrets.token_urlsafe(24);de=d if n<50 else d2
  u=Usuario.objects.create(username=TAG.lower()+str(n),first_name='Carga ficticia',email=TAG.lower()+str(n)+'@example.test',password=make_password(pw),rol=role,delegacion=de)
  u.delegaciones.add(de);accounts.append({'username':u.username,'password':pw,'id':u.id})
 for start in range(0,10100,500):
  Atencion.objects.bulk_create([Atencion(folio=TAG+'-'+str(n),solicitante=TAG+' Persona ficticia '+str(n),descripcion=TAG+(' G1' if n<5000 else ' G2')+' Lote QA',tipo_atencion=t,sub_atencion=s,usuario_id=accounts[0]['id'] if n<10000 else accounts[50]['id'],delegacion=d if n<10000 else d2,clave_idempotencia=TAG+'-seed-'+str(n)) for n in range(start,min(start+500,10100))])
p=Path('/home/ubuntu/ren-private.json');p.write_text(json.dumps({'tag':TAG,'accounts':accounts,'delegacion':d.id,'delegacion_ajena':d2.id,'tipo':t.id,'sub':s.id,'seed_d01':10000,'seed_d02':100}));p.chmod(0o600)
print(json.dumps({'tag':TAG,'cuentas':len(accounts),'d01':10000,'d02':100}))
