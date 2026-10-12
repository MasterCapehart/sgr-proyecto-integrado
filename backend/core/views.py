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
    Ejemplo real conectado de implementación del Patrón Común de CRUD (Tarea T04).
    Gestiona el catálogo de Tipos de Atención mediante el contrato estándar.
    """
    model = TipoAtencion
    fields = ["codigo", "nombre", "descripcion", "estado"]
    search_fields = ["codigo", "nombre", "descripcion"]
    ordering = ["codigo"]


class DelegacionCRUDView(BaseCRUDView):
    """
    Vista de referencia para el CRUD de Delegaciones (Tarea T13 asignada a Matías).
    Demuestra la reusabilidad directa del patrón común.
    """
    model = Delegacion
    fields = ["nombre", "direccion", "comuna", "estado"]
    search_fields = ["nombre", "direccion", "comuna"]
    ordering = ["nombre"]
