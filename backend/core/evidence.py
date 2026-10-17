"""Registro reproducible de cada caso automatizado, sin atribuir revisiones humanas."""
import csv,json,time,unittest
from pathlib import Path
from datetime import datetime,timezone
from django.test.runner import DiscoverRunner
ROOT=Path(__file__).resolve().parents[2]/'docs/avance-local'

class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.rows=[]
    def startTest(self,test):self.started=time.monotonic();super().startTest(test)
    def record(self,test,status,detail=''):
        self.rows.append({'requisito':'A1–A3 / contrato local','modulo':type(test).__name__,'caso':test.id(),'precondiciones':'Base temporal aislada, fixtures del setUp','pasos':'Ejecutar '+test.id(),'esperado':test.shortDescription() or test._testMethodName,'obtenido':detail or 'Se cumplen las aserciones del caso','estado':status,'responsable':'Ejecución automatizada local; revisión humana pendiente','fecha':datetime.now(timezone.utc).isoformat(),'evidencia':'pruebas-backend.log','duracion_s':round(time.monotonic()-self.started,3)})
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'Aprobado')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'Fallido',str(err[1]))
    def addError(self,test,err):super().addError(test,err);self.record(test,'Fallido',str(err[1]))
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'No ejecutado',reason)
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        self.record(subtest,"Fallido" if err else "Aprobado",str(err[1]) if err else "Variante comprobada: "+subtest.id())
    def stopTestRun(self):
        ROOT.mkdir(parents=True,exist_ok=True)
        (ROOT/'resultados-funcionales.json').write_text(json.dumps(self.rows,ensure_ascii=False,indent=2))
        if self.rows:
            with (ROOT/'matriz-pruebas.csv').open('w',newline='',encoding='utf-8-sig') as f:
                writer=csv.DictWriter(f,fieldnames=self.rows[0].keys());writer.writeheader();writer.writerows(self.rows)
        super().stopTestRun()

class EvidenceRunner(DiscoverRunner):
    def get_test_runner_kwargs(self):return {**super().get_test_runner_kwargs(),'resultclass':Result}
