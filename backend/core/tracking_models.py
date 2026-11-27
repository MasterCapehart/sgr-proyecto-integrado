"""Identidad común de una gestión; el compromiso solo conserva su seguimiento."""
import uuid
from django.conf import settings
from django.db import models

def gestion_code():return 'GES-'+uuid.uuid4().hex[:20].upper()

class RegistroGestion(models.Model):
 codigo=models.CharField(max_length=36,unique=True,default=gestion_code,editable=False)
 delegacion=models.ForeignKey('core.Delegacion',on_delete=models.PROTECT)
 autor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='+')
 tipo=models.CharField(max_length=30,default='Solicitud')
 fecha_solicitud=models.DateField(null=True,blank=True)
 descripcion=models.TextField(max_length=5000)
 solicitante=models.CharField(max_length=200,blank=True)
 telefono=models.CharField(max_length=20,blank=True)
 rut=models.CharField(max_length=12,blank=True)
 sector=models.CharField(max_length=150,blank=True)
 vecino=models.ForeignKey('core.Vecino',on_delete=models.PROTECT,null=True,blank=True)
 territorio_catalogo=models.ForeignKey('core.Territorio',on_delete=models.PROTECT,null=True,blank=True)
 creado=models.DateTimeField(auto_now_add=True)
 actualizado=models.DateTimeField(auto_now=True)
 version=models.PositiveIntegerField(default=1)
