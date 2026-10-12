from django.contrib import admin
from .models import Usuario, Rol, Delegacion, TipoAtencion

admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(Delegacion)
admin.site.register(TipoAtencion)