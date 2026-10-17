"""Panel técnico de consulta. Las escrituras pasan por la API validada y auditada."""
from django.contrib import admin
from .models import Usuario, Rol, Delegacion, TipoAtencion, SubAtencion, ItemMeta, ConfiguracionMeta, PeriodoGestion, Atencion, AuditoriaDerivacion

class ConsultaTecnica(admin.ModelAdmin):
    exclude = ('password', 'codigo_recuperacion', 'correo_unico')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

for model in [Usuario,Rol,Delegacion,TipoAtencion,SubAtencion,ItemMeta,ConfiguracionMeta,PeriodoGestion,Atencion,AuditoriaDerivacion]:
    admin.site.register(model,ConsultaTecnica)
