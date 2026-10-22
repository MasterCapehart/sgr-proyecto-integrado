"""Planificación interna de hitos: separada de la ejecución ciudadana puntuable."""
import uuid
from django.conf import settings
from django.db import models

ESTADOS_HITO = ['Planificado', 'En preparación', 'En ejecución', 'Finalizado', 'Cancelado']

class Hito(models.Model):
    delegacion = models.ForeignKey('core.Delegacion', on_delete=models.PROTECT)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=5000)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField(null=True, blank=True)
    territorio = models.CharField(max_length=150)
    responsables = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='hitos_asignados')
    recursos = models.JSONField(default=list, blank=True)
    estado = models.CharField(max_length=25, default='Planificado', choices=[(x,x) for x in ESTADOS_HITO])
    recurrente = models.BooleanField(default=False)
    periodicidad = models.CharField(max_length=100, blank=True, default='')
    hito_anterior = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    creado = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=1, editable=False)
    clave_idempotencia = models.CharField(max_length=64, unique=True, default=uuid.uuid4, editable=False)
    captura_hash = models.CharField(max_length=64, editable=False)
    class Meta:
        ordering = ['fecha_inicio', 'pk']

class TareaHito(models.Model):
    hito = models.ForeignKey(Hito, on_delete=models.PROTECT, related_name='tareas')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=5000)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='tareas_hitos')
    fecha_limite = models.DateField()
    porcentaje = models.PositiveSmallIntegerField(default=0)
    compromiso = models.OneToOneField('core.Compromiso', null=True, blank=True, on_delete=models.PROTECT, related_name='tarea_hito')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    creado = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=1, editable=False)
    class Meta:
        ordering = ['fecha_limite', 'pk']
        constraints = [models.CheckConstraint(condition=models.Q(porcentaje__gte=0, porcentaje__lte=100), name='avance_hito_0_100')]

class AvanceHito(models.Model):
    tarea = models.ForeignKey(TareaHito, on_delete=models.PROTECT, related_name='avances')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    porcentaje = models.PositiveSmallIntegerField()
    observacion = models.TextField(max_length=2000)
    creado = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-pk']
