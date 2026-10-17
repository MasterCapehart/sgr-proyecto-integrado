"""Cliente de regresión que envía la versión leída, como el editor del navegador.
Las pruebas de conflictos usan explícitamente django.test.Client sin este adaptador.
"""
import json,re
from django.test import Client as DjangoClient
class Client(DjangoClient):
 def generic(self,method,path,data='',content_type='application/octet-stream',**extra):
  match=re.fullmatch(r'(/api/(?:delegaciones|roles|usuarios|tipos-atencion|subatenciones|items-metas|configuraciones-metas)/\d+/)(toggle-estado/)?',path)
  if match and (method in ['PUT','PATCH','DELETE'] or method=='POST' and match[2]):
   try:payload=json.loads(data or '{}') if content_type=='application/json' else {}
   except (ValueError,TypeError):payload=None
   if isinstance(payload,dict) and '_version' not in payload:
    response=super().generic('GET',match[1])
    if response.status_code==200:
     payload['_version']=response.json()['data']['version'];data=json.dumps(payload);content_type='application/json'
  return super().generic(method,path,data,content_type,**extra)
