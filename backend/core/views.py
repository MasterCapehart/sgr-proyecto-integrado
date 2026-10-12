import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import TipoAtencion, Delegacion
from .api import BaseCRUDView


# ==========================================
# 1. Autenticación (Login / Logout - T05)
# ==========================================

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return JsonResponse({'mensaje': 'Login exitoso', 'usuario': user.username}, status=200)
                else:
                    return JsonResponse({'error': 'Cuenta inactiva'}, status=403)
            else:
                return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
            
    return JsonResponse({'error': 'Método no permitido. Use POST.'}, status=405)


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'mensaje': 'Logout exitoso'}, status=200)
    return JsonResponse({'error': 'Método no permitido. Use POST.'}, status=405)


# ==========================================
# 2. Vistas del Patrón Común de CRUD (T04)
# ==========================================

class TipoAtencionCRUDView(BaseCRUDView):
    """
    CRUD completo de Tipos de Atención (Tarea T14).
    Gestiona el catálogo padre de atención ciudadana con:
    - Validación estricta de duplicados en código y nombre.
    - Protección referencial: impide desactivar o alterar si posee subatenciones hijas activas.
    - Exportación común a formato Excel/CSV.
    """
    model = TipoAtencion
    fields = ["codigo", "nombre", "descripcion", "estado"]
    search_fields = ["codigo", "nombre", "descripcion"]
    ordering = ["codigo"]

    def validate_payload(self, data, instance=None):
        """Valida obligatoriedad y unicidad de código y nombre."""
        errors = super().validate_payload(data, instance=instance)
        
        # Validación de duplicados en código
        codigo = data.get("codigo")
        if codigo:
            qs_codigo = TipoAtencion.objects.filter(codigo__iexact=codigo.strip())
            if instance:
                qs_codigo = qs_codigo.exclude(pk=instance.pk)
            if qs_codigo.exists():
                errors.setdefault("codigo", []).append("Ya existe un tipo de atención con este código.")

        # Validación de duplicados en nombre
        nombre = data.get("nombre")
        if nombre:
            qs_nombre = TipoAtencion.objects.filter(nombre__iexact=nombre.strip())
            if instance:
                qs_nombre = qs_nombre.exclude(pk=instance.pk)
            if qs_nombre.exists():
                errors.setdefault("nombre", []).append("Ya existe un tipo de atención con este nombre.")

        return errors

    def delete(self, request, pk=None, *args, **kwargs):
        """Impide desactivar si posee referencias dependientes activas (Criterio T14)."""
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            from .api import api_error
            return api_error(code="NOT_FOUND", message=f"El tipo de atención con ID {pk} no existe.", status=404)

        if hasattr(instance, "subatenciones") and instance.subatenciones.filter(estado=True).exists():
            from .api import api_error
            return api_error(
                code="HAS_ACTIVE_DEPENDENCIES",
                message="No se puede desactivar este tipo de atención porque posee subatenciones activas asociadas. Desactive primero las subatenciones hijas.",
                status=400
            )

        return super().delete(request, pk=pk, *args, **kwargs)

    def toggle_estado(self, request, pk):
        """Impide alternar a inactivo si posee referencias dependientes activas (Criterio T14)."""
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            from .api import api_error
            return api_error(code="NOT_FOUND", message=f"El tipo de atención con ID {pk} no existe.", status=404)

        # Si actualmente está activo y se solicita cambiar a inactivo
        if instance.estado:
            if hasattr(instance, "subatenciones") and instance.subatenciones.filter(estado=True).exists():
                from .api import api_error
                return api_error(
                    code="HAS_ACTIVE_DEPENDENCIES",
                    message="No se puede desactivar este tipo de atención porque posee subatenciones activas asociadas. Desactive primero las subatenciones vinculadas.",
                    status=400
                )

        return super().toggle_estado(request, pk)


class DelegacionCRUDView(BaseCRUDView):
    """
    Vista de referencia para el CRUD de Delegaciones (Tarea T13 asignada a Matías).
    Demuestra la reusabilidad directa del patrón común.
    """
    model = Delegacion
    fields = ["nombre", "direccion", "comuna", "estado"]
    search_fields = ["nombre", "direccion", "comuna"]
    ordering = ["nombre"]
