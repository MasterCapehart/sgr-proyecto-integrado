import json
import random
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

from .models import Usuario, TipoAtencion, Delegacion
from .api import BaseCRUDView

# ==========================================
# 1. Autenticación y Recuperación
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


@csrf_exempt
def solicitar_recuperacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'error': 'El correo es obligatorio'}, status=400)
            
            # Buscar si el usuario existe
            usuario = Usuario.objects.filter(email=email).first()
            
            if usuario:
                # Generar código de 6 dígitos
                codigo = str(random.randint(100000, 999999))
                usuario.codigo_recuperacion = codigo
                usuario.save()
                
                # Simular el envío del correo en la consola
                send_mail(
                    'Código de Recuperación - SGR',
                    f'Hola {usuario.username},\n\nTu código de recuperación es: {codigo}\n\nSi no solicitaste esto, ignora este correo.',
                    'soporte@sgr.cl',
                    [email],
                    fail_silently=False,
                )
            
            # Siempre devolvemos el mismo mensaje por seguridad (evita enumeración de usuarios)
            return JsonResponse({'mensaje': 'Si el correo está registrado, recibirás un código pronto.'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
            
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