"""Fila exclusiva para serializar reservas por funcionario entre delegaciones."""
from django.conf import settings
from django.db import models

class ControlCupoFuncionario(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL,primary_key=True,on_delete=models.PROTECT,related_name='control_cupos')
    creado = models.DateTimeField(auto_now_add=True)
