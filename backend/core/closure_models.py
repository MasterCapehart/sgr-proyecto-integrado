"""Historial y controles locales; no contiene el motor de cálculo de desempeño."""
from django.db import models
from django.conf import settings

class VersionCatalogo(models.Model):
    recurso=models.CharField(max_length=40)
    registro=models.PositiveIntegerField()
    version=models.PositiveIntegerField()
    datos=models.JSONField()
    fecha=models.DateTimeField(auto_now_add=True)
    autor=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.PROTECT)
    observada=models.BooleanField(default=False)
    class Meta:
        ordering=['-version']
        constraints=[models.UniqueConstraint(fields=['recurso','registro','version'],name='version_catalogo_unica')]

class PoliticaOperativa(models.Model):
    version=models.PositiveIntegerField(unique=True)
    transiciones=models.JSONField()
    motivo=models.TextField(max_length=2000)
    fecha=models.DateTimeField(auto_now_add=True)
    autor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    validada=models.BooleanField(default=False)
    alcance=models.CharField(max_length=30,default='Pruebas locales')
    permisos_snapshot=models.JSONField(default=list)

class CierreCompromiso(models.Model):
    compromiso=models.ForeignKey('core.Compromiso',on_delete=models.PROTECT,related_name='cierres')
    autor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    fecha=models.DateTimeField(auto_now_add=True)
    fecha_plazo=models.DateField()
    dias_atraso=models.PositiveIntegerField()
    observacion=models.TextField(max_length=2000)

class AlertaLocal(models.Model):
    clave=models.CharField(max_length=200,unique=True)
    delegacion=models.ForeignKey('core.Delegacion',on_delete=models.PROTECT)
    responsable=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='+')
    recurso=models.CharField(max_length=30)
    registro=models.PositiveIntegerField()
    tipo=models.CharField(max_length=30)
    motivo=models.CharField(max_length=400)
    fecha=models.DateTimeField(auto_now_add=True)
    fecha_referencia=models.DateField(null=True)
    activa=models.BooleanField(default=True)
    resuelta_en=models.DateTimeField(null=True)
    revisada_por=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,related_name='+')
    revisada_en=models.DateTimeField(null=True)
    version=models.PositiveIntegerField(default=1)
    class Meta:
        ordering=['-id']
