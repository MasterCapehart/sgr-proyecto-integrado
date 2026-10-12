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


class Atencion(models.Model):
    """
    Registro transaccional de Atención Ciudadana (Tarea T17).
    Registra la solicitud del ciudadano con autor, fecha y delegación asignados
    por el servidor para garantizar la inmutabilidad institucional.
    """
    folio = models.CharField(max_length=64, unique=True, db_index=True)
    solicitante = models.CharField(max_length=200)
    tipo_atencion = models.ForeignKey(
        TipoAtencion,
        on_delete=models.PROTECT,
        related_name='atenciones'
    )
    sub_atencion = models.ForeignKey(
        SubAtencion,
        on_delete=models.PROTECT,
        related_name='atenciones'
    )
    descripcion = models.TextField()
    delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.PROTECT,
        related_name='atenciones_origen'
    )
    delegacion_responsable = models.ForeignKey(
        Delegacion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='atenciones_responsable'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='atenciones_creadas'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    caso_social = models.CharField(max_length=50, null=True, blank=True)
    numero_gestion = models.PositiveSmallIntegerField(default=1, null=True, blank=True)
    clave_idempotencia = models.CharField(max_length=64, unique=True, null=True, blank=True)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Atención Ciudadana'
        verbose_name_plural = 'Atenciones Ciudadanas'
        ordering = ['-id']

    @property
    def codigo_atencion(self):
        return self.folio

    def __str__(self):
        return f"{self.folio} - {self.solicitante}"