"""Versiones del catálogo de clasificación, sin cálculo de puntaje."""
import uuid
from django.conf import settings
from django.db import models

CLASIFICACIONES = ['Coordinación','Ejecución','Otra gestión']

class ReglaActividad(models.Model):
    delegacion = models.ForeignKey('core.Delegacion', on_delete=models.PROTECT)
    item = models.ForeignKey('core.ItemMeta', on_delete=models.PROTECT, related_name='reglas_clasificacion')
    version = models.PositiveIntegerField()
    clasificacion = models.CharField(max_length=25, choices=[(x,x) for x in CLASIFICACIONES])
    valida_para_puntuar = models.BooleanField(default=False)
    motivo = models.TextField(max_length=2000)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    creado = models.DateTimeField(auto_now_add=True)
    clave_idempotencia = models.CharField(max_length=64, unique=True, default=uuid.uuid4, editable=False)
    captura_hash = models.CharField(max_length=64, editable=False)
    class Meta:
        ordering = ['-version','-pk']
        constraints = [models.UniqueConstraint(fields=['delegacion','item','version'],name='regla_actividad_version_unica')]
