"""Registros operativos locales. No implementa el motor de cálculo SGR."""
import uuid
from django.db import models
from django.conf import settings

def codigo():
    return str(uuid.uuid4())

def ruta_evidencia(instance, filename):
    return f'evidencias/{uuid.uuid4().hex}/{uuid.uuid4().hex}'

class Cargo(models.Model):
    planilla = models.CharField(max_length=20,blank=True,default='',choices=[(x,x) for x in ['AP_ADM','COOR_DISERCO','T_OC','G_SOC','PLAN_CON','GES_SEG']])
    version = models.PositiveIntegerField(default=1, editable=False)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    area = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    def __str__(self): return self.nombre

class RegistroOperativo(models.Model):
    version = models.PositiveIntegerField(default=1, editable=False)
    delegacion = models.ForeignKey('core.Delegacion', on_delete=models.PROTECT)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    creado = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True
        ordering = ['-id']

class Compromiso(RegistroOperativo):
    unidad = models.PositiveIntegerField(default=1)
    codigo_verificacion_foto = models.CharField(max_length=100,blank=True,default='')
    cierre_actual = models.ForeignKey("core.CierreCompromiso",null=True,blank=True,on_delete=models.PROTECT,related_name="+")
    fecha_solicitud = models.DateField(null=True, blank=True)
    folio = models.CharField(max_length=36, unique=True, default=codigo, editable=False)
    descripcion = models.TextField(max_length=5000)
    solicitante = models.CharField(max_length=200)
    sector = models.CharField(max_length=150)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='compromisos_asignados')
    fecha_comprometida = models.DateField()
    area_apoyo = models.CharField(max_length=150)
    origen = models.CharField(max_length=10, choices=[('Interno','Interno'),('Externo','Externo')])
    estado = models.CharField(max_length=20, default='Ingresado', choices=[(x,x) for x in ['Ingresado','Pendiente','En proceso','Realizado']])

class Actividad(RegistroOperativo):
    junta_vecinos = models.CharField(max_length=200, blank=True, default="")
    atencion = models.OneToOneField("core.Atencion", null=True, blank=True, on_delete=models.PROTECT, related_name="actividad_origen")
    clave_idempotencia = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)
    captura_hash = models.CharField(max_length=64, blank=True, default='', editable=False)
    profesional = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT,related_name='actividades_profesional')
    plantilla = models.CharField(max_length=20,blank=True,default='',editable=False)
    unidad = models.PositiveIntegerField(default=1)
    catalogos_snapshot = models.JSONField(null=True, blank=True, editable=False)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, null=True, blank=True)
    derivado_a = models.CharField(max_length=200, blank=True, default='')
    estado_derivacion = models.CharField(max_length=20, default='Sin derivar', choices=[(x,x) for x in ['Sin derivar','Pendiente','En proceso','Resuelta']])

    codigo = models.CharField(max_length=36, unique=True, default=codigo, editable=False)
    fecha = models.DateField()
    solicitud = models.TextField(max_length=5000)
    accion = models.TextField(max_length=5000)
    contacto = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    sector = models.CharField(max_length=150)
    item = models.ForeignKey('core.ItemMeta', on_delete=models.PROTECT)
    compromiso = models.ForeignKey(Compromiso, on_delete=models.PROTECT, null=True, blank=True, related_name='actividades')
    estado = models.CharField(max_length=25, default='Borrador', choices=[(x,x) for x in ['Borrador','Pendiente','Validada','Corrección','Rechazada']])

class Evidencia(RegistroOperativo):
    actividad = models.ForeignKey(Actividad, on_delete=models.PROTECT, related_name='evidencias')
    archivo = models.FileField(upload_to=ruta_evidencia)
    nombre_archivo = models.CharField(max_length=255)
    tipo_mime = models.CharField(max_length=50)
    tamano = models.PositiveIntegerField()
    sha256 = models.CharField(max_length=64)
    descripcion = models.TextField(max_length=2000)
    reemplaza = models.OneToOneField('self', null=True, blank=True, on_delete=models.PROTECT, related_name='siguiente_version')
    estado = models.CharField(max_length=25, default='Pendiente', choices=[(x,x) for x in ['Pendiente','Aprobada','Rechazada','Corrección','Anulada']])

class RevisionEvidencia(models.Model):
    evidencia = models.ForeignKey(Evidencia, on_delete=models.PROTECT, related_name='revisiones')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    decision = models.CharField(max_length=25)
    observacion = models.TextField(max_length=2000)
    version_evidencia = models.PositiveIntegerField()
    class Meta:
        ordering = ['-id']

class SeguimientoCompromiso(models.Model):
    compromiso = models.ForeignKey(Compromiso, on_delete=models.PROTECT, related_name='seguimientos')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    observacion = models.TextField(max_length=2000)
    responsable_anterior = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    responsable_nuevo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    fecha_anterior = models.DateField()
    fecha_nueva = models.DateField()
    class Meta:
        ordering = ['-id']

class Conversacion(models.Model):
    actividad = models.OneToOneField(Actividad, on_delete=models.PROTECT, null=True, blank=True)
    compromiso = models.OneToOneField(Compromiso, on_delete=models.PROTECT, null=True, blank=True)
    evidencia = models.OneToOneField(Evidencia, on_delete=models.PROTECT, null=True, blank=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=(models.Q(actividad__isnull=False, compromiso__isnull=True, evidencia__isnull=True)|models.Q(actividad__isnull=True, compromiso__isnull=False, evidencia__isnull=True)|models.Q(actividad__isnull=True, compromiso__isnull=True, evidencia__isnull=False)), name='conversacion_contexto_unico')]

class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.PROTECT, related_name='mensajes')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    contenido = models.TextField(max_length=2000)
    class Meta:
        ordering = ['id']


class DerivacionActividad(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.PROTECT, related_name='derivaciones')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    destino = models.CharField(max_length=200)
    motivo = models.TextField(max_length=2000)
    estado = models.CharField(max_length=20, choices=[(x,x) for x in ['Pendiente','En proceso','Resuelta']])
    class Meta:
        ordering = ['-id']
