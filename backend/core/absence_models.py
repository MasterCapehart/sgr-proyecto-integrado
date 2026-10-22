"""Disponibilidad laboral explícita; sin documentos clínicos ni cálculo de puntos."""
from django.db import models
from .domain_models import RegistroOperativo
JORNADAS=['No laboral','Completa','Mañana','Tarde']
TIPOS=['Día libre','Vacaciones','Día administrativo','Licencia','Otra ausencia justificada']
class CalendarioFuncionario(RegistroOperativo):
    funcionario=models.ForeignKey('core.Usuario',on_delete=models.PROTECT,related_name='calendarios_laborales')
    periodo=models.ForeignKey('core.PeriodoGestion',on_delete=models.PROTECT,related_name='calendarios_funcionarios')
    semana=models.JSONField()
    no_laborables=models.JSONField(default=list,blank=True)
    metas_prorrateables=models.JSONField(default=list,blank=True)
    motivo=models.CharField(max_length=500)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['delegacion','funcionario','periodo'],name='calendario_funcionario_periodo_delegacion_unico')]
class AusenciaFuncionario(RegistroOperativo):
    calendario=models.ForeignKey(CalendarioFuncionario,on_delete=models.PROTECT,related_name='ausencias')
    tipo=models.CharField(max_length=40,choices=[(x,x) for x in TIPOS])
    inicio=models.DateField()
    fin=models.DateField()
    jornada=models.CharField(max_length=15,choices=[(x,x) for x in JORNADAS if x!='No laboral'])
    justificacion=models.CharField(max_length=500)
    estado=models.CharField(max_length=15,default='Autorizada',choices=[('Autorizada','Autorizada'),('Anulada','Anulada')])
    class Meta:
        constraints=[models.CheckConstraint(condition=models.Q(fin__gte=models.F('inicio')),name='ausencia_fechas_ordenadas')]
