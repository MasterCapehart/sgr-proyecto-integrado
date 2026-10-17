import json,time,threading,urllib.request,urllib.error,http.cookiejar,concurrent.futures,random,statistics,collections,hashlib
from pathlib import Path
from io import BytesIO
from openpyxl import load_workbook
ROOT=Path('.integracion/rendimiento');cfg=json.loads((ROOT/'private.json').read_text());BASE='https://50.17.79.145';TAG=cfg['tag'];stop=threading.Event();lock=threading.Lock();samples=[];created={};issues=[];stage='preparacion'
out=ROOT/'solicitudes.jsonl';out.write_text('')
class Client:
 def __init__(self):self.op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));self.token='';self.seq=0;self.last=None
 def call(self,path,data=None):
  h={'Origin':BASE,'Referer':BASE+'/pages/login.html'}
  if data is not None:h.update({'Content-Type':'application/json','X-CSRFToken':self.token})
  t=time.monotonic();body=None;code=0;size=0;err=''
  try:
   try:r=self.op.open(urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers=h),timeout=15)
   except urllib.error.HTTPError as e:r=e
   raw=r.read();code=r.code;size=len(raw);body=json.loads(raw) if 'application/json' in r.headers.get('Content-Type','') else raw
  except Exception as e:err=type(e).__name__
  return code,body,(time.monotonic()-t)*1000,size,err
 def login(self,a):
  s,b,*_=self.call('/api/csrf/');assert s==200;self.token=b['data']['csrfToken']
  s,b,*_=self.call('/api/login/',{'username':a['username'],'password':a['password']});assert s==200,(s,str(b)[:100])
  s,b,*_=self.call('/api/csrf/');assert s==200;self.token=b['data']['csrfToken']
def record(op,r,expected=(200,),valid=True):
 code,body,ms,size,err=r;row={'time':time.time(),'stage':stage,'operation':op,'status':code,'ms':round(ms,3),'bytes':size,'ok':code in expected and valid,'error':err}
 with lock:
  samples.append(row)
  with out.open('a') as f:f.write(json.dumps(row)+'\n')
 return row['ok']
clients=[]
for a in cfg['accounts']:
 c=Client();c.login(a);clients.append(c)
print('Cuentas independientes autenticadas:',len(clients),flush=True)
# Baselines: first observed (cache unknown), repeat and pagination. No cache flushing.
for term,expected in [(TAG+' G1',5000),(TAG,10000)]:
 for page in (1,1,2,100):
  r=clients[0].call('/api/atenciones/?search='+urllib.parse.quote(term)+'&page_size=50&page='+str(page))
  assert record('consulta_base',r,valid=isinstance(r[1],dict) and r[1].get('count')==expected),(term,r[0],str(r[1])[:100])
r=clients[50].call('/api/atenciones/?search='+TAG);assert record('aislamiento_D02',r,valid=r[1].get('count')==100)
print('Lotes 5.000/10.000 y separación D02 comprobados.',flush=True)
def worker(i,end):
 c=clients[i];rng=random.Random(i+int(end));n=0
 while time.monotonic()<end and not stop.is_set():
  q=rng.random();n+=1
  if q<.5:
   r=c.call('/api/atenciones/?search='+TAG+'&page_size=25&page='+str(rng.randint(1,20)));record('consulta_filtro_pagina',r)
  elif q<.7:record('tablero',c.call('/api/indicadores/'))
  elif q<.9:
   c.seq+=1;key=TAG+'-vu'+str(i)+'-'+str(c.seq);p={'solicitante':TAG+' VU '+str(i),'descripcion':'Registro QA de carga '+key,'tipo_atencion':cfg['tipo'],'sub_atencion':cfg['sub'],'clave_idempotencia':key};r=c.call('/api/atenciones/',p)
   if record('registro',r,(201,200)) and isinstance(r[1],dict) and r[1].get('data'):
    with lock:created[key]=r[1]['data']['id']
    c.last=(p,r[1]['data']['id'])
  else:
   if c.last:
    p,pk=c.last;r=c.call('/api/atenciones/',p);valid=isinstance(r[1],dict) and r[1].get('data',{}).get('id')==pk
    if not valid:
     with lock:issues.append('Idempotencia incorrecta VU '+str(i))
     stop.set()
    record('reenvio_idempotente',r,(200,201),valid)
   else:record('ficha_contexto',c.call('/api/contexto/'))
  stop.wait(1)
def summarize(rows):
 result={}
 for op in sorted({r['operation'] for r in rows}):
  a=[r for r in rows if r['operation']==op];v=sorted(r['ms'] for r in a);pct=lambda p:v[min(len(v)-1,int((len(v)-1)*p))]
  result[op]={'n':len(v),'errores':sum(not r['ok'] for r in a),'promedio_ms':round(statistics.mean(v),2),'p95_ms':pct(.95),'p99_ms':pct(.99),'max_ms':max(v),'exceden_2s':sum(x>2000 for x in v),'exceden_5s':sum(x>5000 for x in v)}
 return result
def export():
 r=clients[49].call('/api/atenciones/export/?search='+TAG);ok=r[0]==200 and isinstance(r[1],bytes)
 if ok:
  (ROOT/'exportacion.xlsx').write_bytes(r[1]);book=load_workbook(BytesIO(r[1]),read_only=True);count=sum(1 for _ in book.active.values)-1
  (ROOT/'exportacion.json').write_text(json.dumps({'filas':count,'duracion_ms':r[2],'bytes':r[3],'sha256':hashlib.sha256(r[1]).hexdigest()}));ok=count>=10000
 record('exportacion_concurrente',r,valid=ok)
 print('Exportación simultánea:',ok,flush=True)
stages=[('control',1,120),('normal',10,600),('incremental20',20,300),('estres50',50,300),('recuperacion',1,300)]
summary=[]
for name,users,seconds in stages:
 if stop.is_set() and name!='recuperacion':continue
 if name=='recuperacion':stop.clear()
 stage=name;start=time.monotonic();startwall=time.time();end=start+seconds
 print('INICIO',name,users,seconds,flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=users+1) as pool:
  fut=[pool.submit(worker,i,end) for i in range(users)]
  if name=='normal':fut.append(pool.submit(export))
  while time.monotonic()<end and not stop.is_set():
   time.sleep(5)
   with lock:recent=[r for r in samples if r['stage']==name and r['time']>=time.time()-60]
   if name!='recuperacion' and time.monotonic()-start>=60 and recent and sum(not r['ok'] for r in recent)/len(recent)>.05:
    issues.append('Parada por errores >5% en ventana de 60 segundos: '+name);stop.set();print(issues[-1],flush=True)
  for f in fut:f.result()
 elapsed=time.monotonic()-start;rows=[r for r in samples if r['stage']==name];entry={'stage':name,'usuarios':users,'duracion_real_s':round(elapsed,2),'rps':round(len(rows)/elapsed,3),'metricas':summarize(rows)};summary.append(entry)
 (ROOT/'resumen.json').write_text(json.dumps({'tag':TAG,'base':BASE,'etapas':summary,'incidencias':issues,'registros_confirmados':len(created),'mezcla':'50% consulta,20% tablero,20% registro,10% reenvío idempotente; validación de evidencia no incluida en carga'},indent=2))
 print('FIN',name,'peticiones',len(rows),'errores',sum(not r['ok'] for r in rows),flush=True)
# Fresh login and final reconciliation without deleting evidence.
stage='conciliacion';fresh=Client();fresh.login(cfg['accounts'][0]);r=fresh.call('/api/atenciones/?search='+TAG+'&page_size=1');expected=10000+len(created);valid=r[0]==200 and r[1].get('count')==expected;record('conteo_final',r,valid=valid)
(ROOT/'claves-confirmadas.json').write_text(json.dumps(created))
(ROOT/'conciliacion.json').write_text(json.dumps({'esperado_d01':expected,'obtenido_d01':r[1].get('count') if isinstance(r[1],dict) else None,'coincide':valid,'incidencias':issues},indent=2));assert valid,'Conteos no conciliados'
print('FINAL conteos conciliados:',expected,flush=True)
