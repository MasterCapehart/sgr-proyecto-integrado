from django.contrib import admin
from .models import Usuario, Rol, Delegacion, TipoAtencion, SubAtencion, ItemMeta, ConfiguracionMeta

admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(Delegacion)
admin.site.register(TipoAtencion)
admin.site.register(SubAtencion)
admin.site.register(ItemMeta)
admin.site.register(ConfiguracionMeta)