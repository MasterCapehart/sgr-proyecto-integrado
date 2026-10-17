"""Evidencias de variantes automatizadas; no equivalen a aceptación de los 84 casos."""
import csv, inspect, json, time, unittest
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from django.test.runner import DiscoverRunner
ROOT=Path(__file__).resolve().parents[2]/'docs/revision-local/cierre-local'
class Result(unittest.TextTestResult):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.rows=[]
 def startTest(self,test):self.started=time.monotonic();super().startTest(test)
 def record(self,test,status,detail=''):
  parent=getattr(test,'test_case',test)
  method=getattr(parent,parent._testMethodName)
  source=inspect.getsourcefile(method);line=inspect.getsourcelines(method)[1]
  self.rows.append(dict(variante=test.id(),fuente=f'{Path(source).relative_to(ROOT.parents[2])}:{line}',precondiciones='Base MySQL temporal; fixtures de setUp del caso indicado',pasos='Ejecutar manage.py test '+parent.id(),esperado=test.shortDescription() or parent._testMethodName,obtenido=detail or 'Todas las aserciones ejecutadas se cumplen',estado=status,responsable='Automatización local; aceptación humana pendiente',fecha=datetime.now(ZoneInfo('America/Santiago')).isoformat(),duracion_s=round(time.monotonic()-self.started,3)))
 def addSuccess(self,test):super().addSuccess(test);self.record(test,'Aprobado automatizado')
 def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'Fallido',str(err[1]))
 def addError(self,test,err):super().addError(test,err);self.record(test,'Error',str(err[1]))
 def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'No ejecutado',reason)
 def addSubTest(self,test,subtest,err):
  super().addSubTest(test,subtest,err)
  if err:self.record(test,'Fallido',str(err[1]))
 def stopTestRun(self):
  ROOT.mkdir(parents=True,exist_ok=True)
  (ROOT/'ejecucion-unittest.json').write_text(json.dumps(self.rows,ensure_ascii=False,indent=2))
  if self.rows:
   with (ROOT/'variantes-automatizadas.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=self.rows[0]);w.writeheader();w.writerows(self.rows)
  super().stopTestRun()
class EvidenceRunner(DiscoverRunner):
 def get_test_runner_kwargs(self):return {**super().get_test_runner_kwargs(),'resultclass':Result}
