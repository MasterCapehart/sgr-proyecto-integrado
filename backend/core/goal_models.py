"""Asignaciones individuales; las configuraciones históricas por cargo se conservan."""
from django.conf import settings
from django.db import models

class AsignacionMeta(models.Model):
    funcionario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='metas_individuales')
    item = models.ForeignKey('core.ItemMeta',on_delete=models.PROTECT,related_name='asignaciones_individuales')
    periodo = models.ForeignKey('core.PeriodoGestion',on_delete=models.PROTECT,related_name='asignaciones_individuales')
    delegacion = models.ForeignKey('core.Delegacion',on_delete=models.PROTECT)
    cantidad_objetivo = models.DecimalField(max_digits=12,decimal_places=2)
    ponderacion = models.DecimalField(max_digits=5,decimal_places=2)
    observacion = models.TextField(max_length=2000,blank=True)
    estado = models.BooleanField(default=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='+')
    snapshot = models.JSONField(default=dict,editable=False)
    version = models.PositiveIntegerField(default=1,editable=False)
    class Meta:
        ordering=['funcionario_id','item_id','pk']
        constraints=[models.UniqueConstraint(fields=['funcionario','item','periodo'],name='meta_individual_unica'),models.CheckConstraint(condition=models.Q(cantidad_objetivo__gt=0),name='meta_individual_objetivo_positivo'),models.CheckConstraint(condition=models.Q(ponderacion__gte=0,ponderacion__lte=100),name='meta_individual_peso_rango')]
