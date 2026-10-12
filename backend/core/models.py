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
    codigo_recuperacion = models.CharField(max_length=6, null=True, blank=True) # <-- Aquí está el campo nuevo
    
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
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class SubAtencion(CatalogoBase):
    """Catálogo hijo vinculado al catálogo padre TipoAtencion (Tarea T14 / T15)."""
    tipo_atencion = models.ForeignKey(
        TipoAtencion,
        on_delete=models.PROTECT,
        related_name='subatenciones'
    )

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.tipo_atencion.codigo})"


class ItemMeta(CatalogoBase):
    """
    Catálogo de Ítems medibles y criterios de evaluación SGR (Tarea T16).
    Mapea a los indicadores y conceptos operativos para el cálculo de resultados.
    """
    unidad_medida = models.CharField(max_length=50, default='Cantidad', blank=True)

    class Meta:
        verbose_name = 'Ítem y Meta'
        verbose_name_plural = 'Ítems y Metas'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class ConfiguracionMeta(models.Model):
    """
    Asignación y alcance de metas por período e ítem medible (Tarea T16).
    Conserva la historia y valida referencias sin fórmulas inventadas.
    """
    item = models.ForeignKey(ItemMeta, on_delete=models.PROTECT, related_name='configuraciones_meta')
    periodo = models.CharField(max_length=50, default='2026-Anual')
    meta_esperada = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    ponderacion = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"Meta {self.item.codigo} ({self.periodo}): {self.meta_esperada}"