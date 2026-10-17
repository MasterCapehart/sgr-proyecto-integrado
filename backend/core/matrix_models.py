"""Captura de los dos bloques de RECLAMOS; sin puntajes ni trabajadores importados."""
from django.db import models
from .domain_models import RegistroOperativo,codigo
class Reclamo(RegistroOperativo):
    folio=models.CharField(max_length=36,unique=True,default=codigo,editable=False)
    clase=models.CharField(max_length=20,choices=[('Reclamo','Reclamo'),('Felicitación','Felicitación')])
    fecha=models.DateField()
    vecino=models.CharField(max_length=200)
    contacto=models.CharField(max_length=100,blank=True)
    ubicacion=models.CharField(max_length=250,blank=True)
    situacion=models.TextField(max_length=5000)
    profesional=models.ForeignKey('core.Usuario',null=True,blank=True,on_delete=models.PROTECT,related_name='reclamos_involucrado')
    medio_escrito=models.BooleanField(default=False)
    informado_a=models.CharField(max_length=200,blank=True)
    evidencia=models.ForeignKey('core.Evidencia',null=True,blank=True,on_delete=models.PROTECT,related_name='reclamos')
