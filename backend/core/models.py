from django.db import models
from django.contrib.auth.models import AbstractUser

class Delegacion(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    comuna = models.CharField(max_length=100, default='Coquimbo')
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    # Heredamos de AbstractUser para aprovechar el login de Django
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    delegacion = models.ForeignKey(Delegacion, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"

class CatalogoBase(models.Model):
    """Modelo abstracto para reutilizar en otros catálogos como Tipos de Atención"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        abstract = True

class TipoAtencion(CatalogoBase):
    pass