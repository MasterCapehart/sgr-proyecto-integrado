import json
import random
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

from .models import Usuario, TipoAtencion, SubAtencion, Delegacion
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


class SubAtencionCRUDView(BaseCRUDView):
    """
    CRUD completo de Subatenciones (catálogo hijo - Tarea T15).
    Gestiona el catálogo dependiente de TipoAtencion con:
    - Validación de catálogo padre obligatorio y activo.
    - Control de duplicados en código y nombre.
    - Búsqueda por código, nombre y catálogo padre.
    - Exportación a Excel/CSV con el nombre del tipo padre.
    """
    model = SubAtencion
    fields = ["codigo", "nombre", "descripcion", "tipo_atencion", "estado"]
    search_fields = ["codigo", "nombre", "descripcion", "tipo_atencion__codigo", "tipo_atencion__nombre"]
    ordering = ["codigo"]

    def get_queryset(self):
        return SubAtencion.objects.select_related("tipo_atencion").all()

    def serialize_instance(self, instance):
        data = super().serialize_instance(instance)
        if instance.tipo_atencion:
            data["tipo_atencion"] = instance.tipo_atencion.pk
            data["tipo_atencion_codigo"] = instance.tipo_atencion.codigo
            data["tipo_atencion_nombre"] = instance.tipo_atencion.nombre
            data["tipo_padre_display"] = f"{instance.tipo_atencion.codigo} · {instance.tipo_atencion.nombre}"
        else:
            data["tipo_atencion"] = None
            data["tipo_padre_display"] = "Sin asignar"
        return data

    def validate_payload(self, data, instance=None):
        errors = {}

        # 1. Resolver y validar tipo_atencion (catálogo padre)
        tipo_id = data.get("tipo_atencion") or data.get("tipo_padre")
        parent_obj = None

        if not tipo_id:
            errors.setdefault("tipo_atencion", []).append("Debe seleccionar un Tipo de Atención (catálogo padre).")
        else:
            if str(tipo_id).isdigit():
                parent_obj = TipoAtencion.objects.filter(pk=int(tipo_id)).first()
            else:
                cod_candidate = str(tipo_id).split("·")[0].strip()
                parent_obj = TipoAtencion.objects.filter(codigo__iexact=cod_candidate).first()

            if not parent_obj:
                errors.setdefault("tipo_atencion", []).append("El Tipo de Atención indicado no existe.")
            elif not parent_obj.estado:
                # Regla T15: El catálogo padre debe estar activo
                errors.setdefault("tipo_atencion", []).append("El Tipo de Atención seleccionado está inactivo. Debe estar activo para asociarle subatenciones.")

        if parent_obj:
            data["tipo_atencion"] = parent_obj

        # 2. Validar campos requeridos y unicidad
        codigo = data.get("codigo")
        if not codigo:
            errors.setdefault("codigo", []).append("El código es obligatorio.")
        else:
            qs_cod = SubAtencion.objects.filter(codigo__iexact=str(codigo).strip())
            if instance:
                qs_cod = qs_cod.exclude(pk=instance.pk)
            if qs_cod.exists():
                errors.setdefault("codigo", []).append("Ya existe una subatención con este código.")

        nombre = data.get("nombre")
        if not nombre:
            errors.setdefault("nombre", []).append("El nombre es obligatorio.")
        elif parent_obj:
            qs_nom = SubAtencion.objects.filter(
                tipo_atencion=parent_obj,
                nombre__iexact=str(nombre).strip()
            )
            if instance:
                qs_nom = qs_nom.exclude(pk=instance.pk)
            if qs_nom.exists():
                errors.setdefault("nombre", []).append(f"Ya existe una subatención con este nombre bajo el tipo {parent_obj.codigo}.")

        return errors

    def export(self, request):
        """Exporta subatenciones a CSV compatible con Excel."""
        import csv
        from django.http import HttpResponse

        qs = self.filter_queryset(self.get_queryset())
        filename = "subatenciones_export.csv"

        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(["ID", "Código", "Nombre de la Subatención", "Tipo de Atención Padre", "Estado"])

        for item in qs:
            padre_str = f"{item.tipo_atencion.codigo} · {item.tipo_atencion.nombre}" if item.tipo_atencion else ""
            writer.writerow([
                item.pk,
                item.codigo,
                item.nombre,
                padre_str,
                "Activo" if item.estado else "Inactivo"
            ])

        return response
