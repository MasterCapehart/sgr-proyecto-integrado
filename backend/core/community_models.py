"""Organizaciones y pertenencias; la desactivación conserva referencias históricas."""
import uuid
from django.db import models

class OrganizacionComunitaria(models.Model):
 delegacion=models.ForeignKey('core.Delegacion',on_delete=models.PROTECT,related_name='organizaciones')
 tipo=models.CharField(max_length=40,choices=[('Junta de vecinos','Junta de vecinos'),('Organización comunitaria','Organización comunitaria')])
 nombre=models.CharField(max_length=200,db_index=True)
 domicilio_legal=models.CharField(max_length=250,blank=True,default='')
 territorio=models.CharField(max_length=150)
 socios_activos=models.PositiveIntegerField(null=True,blank=True)
 fecha_constitucion=models.DateField(null=True,blank=True)
 registro_personalidad_juridica=models.CharField(max_length=100,blank=True,default='')
 fecha_inscripcion=models.DateField(null=True,blank=True)
 numero_registro=models.CharField(max_length=100,blank=True,default='')
 activo=models.BooleanField(default=True)
 version=models.PositiveIntegerField(default=1,editable=False)
 creado_por=models.ForeignKey('core.Usuario',on_delete=models.PROTECT,related_name='+')
 creado=models.DateTimeField(auto_now_add=True)
 clave_idempotencia=models.CharField(max_length=64,unique=True,default=uuid.uuid4,editable=False)
 captura_hash=models.CharField(max_length=64,editable=False)
 class Meta:ordering=['nombre','pk']

class PertenenciaOrganizacion(models.Model):
 vecino=models.ForeignKey('core.Vecino',on_delete=models.PROTECT,related_name='pertenencias')
 organizacion=models.ForeignKey(OrganizacionComunitaria,on_delete=models.PROTECT,related_name='pertenencias')
 rol=models.CharField(max_length=20,choices=[('Integrante','Integrante'),('Dirigente','Dirigente')])
 activo=models.BooleanField(default=True)
 version=models.PositiveIntegerField(default=1,editable=False)
 creado_por=models.ForeignKey('core.Usuario',on_delete=models.PROTECT,related_name='+')
 creado=models.DateTimeField(auto_now_add=True)
 class Meta:
  ordering=['pk']
  constraints=[models.UniqueConstraint(fields=['vecino','organizacion'],name='pertenencia_vecino_organizacion_unica')]
