"""DF28–30. Transiciones operativas elegidas explícitamente para el flujo mínimo."""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from pathlib import Path

STATES=['Ingresada','Derivada','En proceso','Aprobada','Finalizada','No aplica']
TRANSITIONS={'Ingresada':['Derivada','En proceso','No aplica'],'Derivada':['En proceso','No aplica'],'En proceso':['Derivada','Aprobada','Finalizada','No aplica'],'Aprobada':['Finalizada','En proceso'],'Finalizada':[],'No aplica':[]}
def code():return 'CAR-'+uuid.uuid4().hex.upper()
def validate_transition(old,new):
    if new not in TRANSITIONS.get(old,[]):raise ValidationError('Transición de estado no permitida.')
def private_storage():return FileSystemStorage(location=Path(settings.MEDIA_ROOT).parent/'private-cartas',base_url=None)
def document_path(instance,name):return f'cartas/{instance.carta_id}/{uuid.uuid4().hex}'
class Carta(models.Model):
    codigo=models.CharField(max_length=36,unique=True,default=code,editable=False)
    delegacion=models.ForeignKey('core.Delegacion',on_delete=models.PROTECT)
    numero_carta=models.CharField(max_length=100)
    fecha=models.DateField()
    remitente=models.CharField(max_length=200)
    destinatario=models.CharField(max_length=200)
    telefono=models.CharField(max_length=30,blank=True)
    materia=models.TextField()
    fecha_respuesta=models.DateField(null=True,blank=True)
    responsable=models.ForeignKey('core.Usuario',on_delete=models.PROTECT,related_name='cartas_responsables')
    area_derivada=models.CharField(max_length=200,blank=True)
    estado=models.CharField(max_length=20,choices=[(s,s) for s in STATES],default='Ingresada')
    pronunciamiento=models.TextField(blank=True)
    observaciones=models.TextField(blank=True)
    fecha_cierre=models.DateField(null=True,blank=True)
    version=models.PositiveIntegerField(default=1,editable=False)
    creado_por=models.ForeignKey('core.Usuario',on_delete=models.PROTECT,related_name='+')
    creado=models.DateTimeField(auto_now_add=True)
    clave_idempotencia=models.CharField(max_length=64,unique=True,editable=False)
    captura_hash=models.CharField(max_length=64,editable=False)
    class Meta:ordering=['-fecha','-pk']
    def clean(self):
        if self.estado in ['Finalizada','No aplica'] and (not self.pronunciamiento.strip() or not self.fecha_cierre):raise ValidationError('El cierre requiere pronunciamiento o resultado y fecha de cierre.')
        if self.estado not in ['Finalizada','No aplica'] and self.fecha_cierre:raise ValidationError('La fecha de cierre requiere estado terminal.')
        if self.fecha_cierre and self.fecha and str(self.fecha_cierre)<str(self.fecha):raise ValidationError('El cierre no puede preceder al ingreso.')
    def save(self,*a,**kw):
        if self.pk and type(self).objects.filter(pk=self.pk).exclude(codigo=self.codigo).exists():raise ValidationError('El código automático es inmutable.')
        super().save(*a,**kw)
class DocumentoCarta(models.Model):
    carta=models.ForeignKey(Carta,on_delete=models.PROTECT,related_name='documentos')
    archivo=models.FileField(upload_to=document_path,storage=private_storage)
    nombre=models.CharField(max_length=200)
    mime=models.CharField(max_length=50)
    tamano=models.PositiveIntegerField()
    autor=models.ForeignKey('core.Usuario',on_delete=models.PROTECT)
    creado=models.DateTimeField(auto_now_add=True)
