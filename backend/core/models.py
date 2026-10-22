from django.db import models
from django.contrib.auth.models import AbstractUser

class Delegacion(models.Model):
    version = models.PositiveIntegerField(default=1, editable=False)
    codigo = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    comuna = models.CharField(max_length=100, default='La Serena')
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    version = models.PositiveIntegerField(default=1, editable=False)
    permisos = models.JSONField(default=list, blank=True)
    alcance = models.CharField(max_length=20, default="delegacion", choices=[("delegacion", "Delegaciones autorizadas"), ("global", "Global")])
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    cargo = models.ForeignKey("core.Cargo", on_delete=models.PROTECT, null=True, blank=True)
    version = models.PositiveIntegerField(default=1, editable=False)
    delegaciones = models.ManyToManyField(Delegacion, blank=True, related_name="usuarios_autorizados")
    correo_unico = models.CharField(max_length=254, unique=True, null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        self.rut = self.rut or None
        self.email = self.email.strip().lower()
        self.correo_unico = self.email or None
        super().save(*args, **kwargs)

    # Heredamos de AbstractUser para aprovechar el login de Django
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    delegacion = models.ForeignKey(Delegacion, on_delete=models.SET_NULL, null=True, blank=True)
    codigo_recuperacion = models.CharField(max_length=6, null=True, blank=True) # <-- Aquí está el campo nuevo
    # Compatibilidad de la migración remota 0007; el flujo vigente usa RecuperacionAcceso.
    codigo_recuperacion_creado = models.DateTimeField(null=True, blank=True)
    codigo_recuperacion_intentos = models.PositiveSmallIntegerField(default=0)
    
    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"

class CatalogoBase(models.Model):
    version = models.PositiveIntegerField(default=1, editable=False)
    """Modelo abstracto para reutilizar en otros catálogos como Tipos de Atención"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
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
    cargos = models.ManyToManyField("core.Cargo", blank=True, related_name="items")
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


class PeriodoGestion(CatalogoBase):
    """Calendario explícito; cerrado es independiente del estado activo del catálogo."""
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False, editable=False)
    parametros_cierre = models.JSONField(default=dict, blank=True, editable=False)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=models.Q(fecha_fin__gte=models.F('fecha_inicio')),
            name='periodo_fechas_ordenadas',
        )]

    @property
    def duracion_dias(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1

    def __str__(self):
        return f'{self.codigo} · {self.nombre}'


class ConfiguracionMeta(models.Model):
    version = models.PositiveIntegerField(default=1, editable=False)
    """
    Asignación y alcance de metas por período e ítem medible (Tarea T16).
    Conserva la historia y valida referencias sin fórmulas inventadas.
    """
    item = models.ForeignKey(ItemMeta, on_delete=models.PROTECT, related_name='configuraciones_meta')
    periodo = models.CharField(max_length=50, default='2026-Anual')
    periodo_gestion = models.ForeignKey(PeriodoGestion, null=True, blank=True, on_delete=models.PROTECT, related_name='metas')
    conciliada_con = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='duplicados_conciliados', editable=False)
    meta_esperada = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    ponderacion = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    estado = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['item', 'periodo_gestion'], name='meta_unica_item_periodo_gestion')]

    def __str__(self):
        return f"Meta {self.item.codigo} ({self.periodo}): {self.meta_esperada}"


class Atencion(models.Model):
    elegibilidad_snapshot = models.JSONField(null=True, blank=True, editable=False)
    fecha_visita_programada = models.DateField(null=True, blank=True)
    fecha_visita_realizada = models.DateField(null=True, blank=True)
    tipo_gestion = models.CharField(max_length=100, blank=True, default='')
    compromiso = models.ForeignKey('core.Compromiso', null=True, blank=True, on_delete=models.PROTECT, related_name='atenciones_sociales')
    catalogos_snapshot = models.JSONField(null=True, blank=True, editable=False)
    rut_solicitante = models.CharField(max_length=12, blank=True, default='')
    telefono_solicitante = models.CharField(max_length=20, blank=True, default='')
    requiere_visita = models.BooleanField(null=True, blank=True, default=None)
    fecha_visita = models.DateField(null=True, blank=True)
    fecha_entrega_informe = models.DateField(null=True, blank=True)
    fecha_entrega_beneficio = models.DateField(null=True, blank=True)
    gestion_realizada = models.TextField(max_length=2000, blank=True, default='')

    """
    Registro transaccional de Atención Ciudadana (Tarea T17).
    Registra la solicitud del ciudadano con autor, fecha y delegación asignados
    por el servidor para garantizar la inmutabilidad institucional.
    """
    folio = models.CharField(max_length=64, unique=True, db_index=True)
    solicitante = models.CharField(max_length=200, blank=True, default="")
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
    captura_hash = models.CharField(max_length=64, blank=True, default='', editable=False)
    clave_idempotencia = models.CharField(max_length=64, unique=True, null=True, blank=True)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Atención Ciudadana'
        verbose_name_plural = 'Atenciones Ciudadanas'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['caso_social','numero_gestion'], name='caso_gestion_unica_local'),
            models.CheckConstraint(condition=models.Q(numero_gestion__gte=1, numero_gestion__lte=3) | models.Q(numero_gestion__isnull=True), name='gestion_rango_local'),
        ]

    @property
    def codigo_atencion(self):
        return self.folio

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        if self.sub_atencion_id and self.tipo_atencion_id:
            if self.sub_atencion.tipo_atencion_id != self.tipo_atencion_id:
                raise ValidationError({'sub_atencion': 'La subatención no pertenece al tipo de atención indicado.'})
        if self.caso_social and self.numero_gestion is not None:
            if self.numero_gestion < 1 or self.numero_gestion > 3:
                raise ValidationError({'numero_gestion': 'Un caso social solo puede conservar hasta 3 gestiones sucesivas.'})

    def __str__(self):
        return f"{self.folio} - {self.solicitante}"


class AuditoriaDerivacion(models.Model):
    """
    Registro inmutable de auditoría para derivaciones territoriales de atención ciudadana (Tarea T18).
    Permite auditar el traspaso de responsabilidad entre delegaciones municipales.
    """
    atencion = models.ForeignKey(Atencion, on_delete=models.CASCADE, related_name='derivaciones_auditadas')
    delegacion_origen = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='+')
    delegacion_destino = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='+')
    usuario_responsable = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='+')
    motivo = models.CharField(max_length=255, blank=True, default='Derivación institucional autorizada')
    fecha_derivacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auditoría de Derivación'
        verbose_name_plural = 'Auditorías de Derivaciones'
        ordering = ['-fecha_derivacion']

    def __str__(self):
        return f"Derivación {self.atencion.folio}: {self.delegacion_origen.nombre} -> {self.delegacion_destino.nombre}"

class RecuperacionAcceso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    identificador = models.UUIDField(unique=True)
    codigo_hash = models.CharField(max_length=128)
    vence = models.DateTimeField()
    creado = models.DateTimeField(auto_now_add=True)
    intentos = models.PositiveSmallIntegerField(default=0)
    verificado = models.BooleanField(default=False)
    consumido = models.BooleanField(default=False)

class CasoSocial(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    solicitante = models.CharField(max_length=200, blank=True, default="")

class EventoLocal(models.Model):
    antes = models.JSONField(null=True, blank=True)
    despues = models.JSONField(null=True, blank=True)
    origen = models.GenericIPAddressField(null=True, blank=True)
    delegacion = models.ForeignKey(Delegacion, null=True, blank=True, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, null=True, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    recurso = models.CharField(max_length=50)
    registro = models.PositiveIntegerField(null=True)
    accion = models.CharField(max_length=30)


class AccesoFallido(models.Model):
    cuenta_hash = models.CharField(max_length=64, db_index=True)
    direccion_hash = models.CharField(max_length=64, db_index=True)
    creado = models.DateTimeField(auto_now_add=True, db_index=True)

class Vecino(models.Model):
    direccion = models.CharField(max_length=250, blank=True, default="")
    activo = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1, editable=False)
    delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='vecinos')
    nombre = models.CharField(max_length=200, db_index=True)
    rut = models.CharField(max_length=12, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, default='')
    sector = models.CharField(max_length=150, blank=True, default='')
    junta_vecinos = models.CharField(max_length=200, blank=True, default='')
    creado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='vecinos_registrados')
    creado = models.DateTimeField(auto_now_add=True)
    clave_idempotencia = models.CharField(max_length=64, unique=True, editable=False)
    captura_hash = models.CharField(max_length=64, editable=False)

    class Meta:
        ordering = ['nombre', 'pk']
        constraints = [models.UniqueConstraint(fields=['delegacion','rut'], name='vecino_rut_delegacion_unico')]

from .domain_models import Cargo, DerivacionActividad, Actividad, Evidencia, RevisionEvidencia, Compromiso, SeguimientoCompromiso, Conversacion, Mensaje
from .closure_models import VersionCatalogo, PoliticaOperativa, CierreCompromiso, AlertaLocal

from .matrix_models import Reclamo,RespaldoFelicitacion,RevisionFelicitacion

from .community_models import OrganizacionComunitaria, PertenenciaOrganizacion

from .milestone_models import Hito, TareaHito, AvanceHito

from .eligibility_models import ReglaActividad

from .registration_models import ControlCupoFuncionario
from .absence_models import CalendarioFuncionario,AusenciaFuncionario
