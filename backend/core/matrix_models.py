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

    procedencia=models.CharField(max_length=25,default='Sin determinar',choices=[(x,x) for x in ['Sin determinar','Directa','Personal','Otra']])
    destinatario=models.CharField(max_length=25,default='Sin determinar',choices=[(x,x) for x in ['Sin determinar','Delegado','Delegación','Funcionario','Otro']])

def ruta_respaldo(instance,filename):
    import uuid
    return 'felicitaciones/'+uuid.uuid4().hex+'/'+uuid.uuid4().hex

class RespaldoFelicitacion(models.Model):
    reclamo=models.ForeignKey(Reclamo,on_delete=models.PROTECT,related_name='respaldos_formales')
    archivo=models.FileField(upload_to=ruta_respaldo)
    nombre=models.CharField(max_length=255)
    tipo_mime=models.CharField(max_length=50)
    tamano=models.PositiveIntegerField()
    sha256=models.CharField(max_length=64)
    autor=models.ForeignKey('core.Usuario',on_delete=models.PROTECT,related_name='+')
    creado=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-pk']

class RevisionFelicitacion(models.Model):
    reclamo=models.ForeignKey(Reclamo,on_delete=models.PROTECT,related_name='revisiones_formales')
    version_registro=models.PositiveIntegerField()
    decision=models.CharField(max_length=20,choices=[('Validada','Validada'),('Rechazada','Rechazada')])
    observacion=models.TextField(max_length=2000)
    respaldo=models.ForeignKey(RespaldoFelicitacion,null=True,blank=True,on_delete=models.PROTECT)
    autor=models.ForeignKey('core.Usuario',on_delete=models.PROTECT,related_name='+')
    creado=models.DateTimeField(auto_now_add=True)
    snapshot=models.JSONField(default=dict)
    class Meta:
        ordering=['-pk']
        constraints=[models.UniqueConstraint(fields=['reclamo','version_registro'],name='felicitacion_revision_version_unica')]
