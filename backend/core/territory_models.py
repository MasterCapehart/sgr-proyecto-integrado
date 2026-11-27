"""Catálogo territorial; los textos originales permanecen como instantáneas."""
import uuid
from django.db import models
from django.core.exceptions import ValidationError

def territory_code():
 return 'TER-'+uuid.uuid4().hex[:12].upper()

class Territorio(models.Model):
 codigo=models.CharField(max_length=20,unique=True,default=territory_code,editable=False)
 nombre=models.CharField(max_length=150)
 nombre_normalizado=models.CharField(max_length=150,editable=False)
 descripcion=models.TextField(blank=True,default='')
 delegacion=models.ForeignKey('core.Delegacion',on_delete=models.PROTECT,related_name='territorios')
 activo=models.BooleanField(default=True)
 version=models.PositiveIntegerField(default=1,editable=False)
 creado=models.DateTimeField(auto_now_add=True)
 actualizado=models.DateTimeField(auto_now=True)
 class Meta:
  ordering=['nombre','pk']
  constraints=[models.UniqueConstraint(fields=['delegacion','nombre_normalizado'],name='territorio_nombre_delegacion_unico')]
 def clean(self):
  self.nombre=' '.join(self.nombre.split())
  self.nombre_normalizado=self.nombre.casefold()
  if not self.nombre:raise ValidationError({'nombre':'Indica el nombre del territorio.'})
  if self.pk:
   old=type(self).objects.get(pk=self.pk)
   if old.codigo!=self.codigo or old.delegacion_id!=self.delegacion_id:raise ValidationError('El código y la delegación del territorio no pueden cambiarse.')
 def save(self,*args,**kwargs):
  self.clean()
  super().save(*args,**kwargs)
 def __str__(self):return self.nombre
