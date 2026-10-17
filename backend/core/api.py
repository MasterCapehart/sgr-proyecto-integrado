import json
import openpyxl
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


def api_success(data=None, message=None, extra=None, status=200):
    """Genera una respuesta exitosa uniforme según el contrato de API."""
    payload = {"success": True}
    if message:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    if extra:
        payload.update(extra)
    return JsonResponse(payload, status=status)


def api_error(code="BAD_REQUEST", message="Ocurrió un error en la solicitud", details=None, status=400):
    """Genera una respuesta de error uniforme según el contrato de API."""
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }
    return JsonResponse(payload, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class BaseCRUDView(View):
    """
    Clase base reusable para vistas CRUD según el Patrón Común de API (Tarea T04).
    Incluye control de acceso centralizado (T08) y exportación a XLSX nativo (T12).

    Provee soporte automático para:
    - Listado paginado con búsqueda (?search=) y filtro de estado (?estado=activos|inactivos|todos).
    - Creación (POST).
    - Consulta de detalle (GET con pk).
    - Actualización parcial/total (PUT / PATCH).
    - Desactivación lógica (DELETE / toggle-estado).
    """
    model = None
    fields = []
    search_fields = []
    ordering = ["-id"]
    default_page_size = 10
    max_page_size = 100
    soft_delete_field = "estado"

    def dispatch(self, request, *args, **kwargs):
        # 1. VERIFICACIÓN DE AUTENTICACIÓN
        if not request.user.is_authenticated:
            return api_error(
                code="UNAUTHORIZED", 
                message="Debe iniciar sesión para acceder a este recurso.", 
                status=401
            )

        # 2. VERIFICACIÓN DE PERMISOS DE ESCRITURA (ROLES)
        # Protegemos métodos que modifican datos
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # Obtenemos el nombre del rol del usuario (protegido contra nulos)
            rol_nombre = getattr(request.user.rol, 'nombre', '').lower() if hasattr(request.user, 'rol') and request.user.rol else ''
            
            # Ejemplo: Si el rol es 'Lector' o 'Ciudadano', bloqueamos la escritura.
            # Puedes ajustar los nombres de los roles según los que hayan creado en su base de datos.
            if rol_nombre in ['lector', 'ciudadano']:
                return api_error(
                    code="FORBIDDEN", 
                    message="Su rol no tiene permisos para modificar o crear registros.", 
                    status=403
                )

        # 3. PARSEO DEL BODY (Manejo original)
        if request.method in ["POST", "PUT", "PATCH"]:
            if request.content_type and "application/json" in request.content_type:
                try:
                    request.json_data = json.loads(request.body.decode("utf-8")) if request.body else {}
                except json.JSONDecodeError:
                    return api_error(
                        code="INVALID_JSON",
                        message="El cuerpo de la solicitud no es un JSON válido.",
                        status=400
                    )
            else:
                request.json_data = request.POST.dict()
        else:
            request.json_data = {}
            
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Retorna el queryset base aplicando el contexto autorizado del usuario.
        Evita que vean o editen registros de otras delegaciones.
        """
        if self.model is None:
            raise NotImplementedError("Debe definir 'model' en la vista CRUD.")
            
        qs = self.model.objects.all()
        user = self.request.user
        
        # Obtenemos el rol para saber si es Administrador Global
        rol_nombre = getattr(user.rol, 'nombre', '').lower() if hasattr(user, 'rol') and user.rol else ''
        
        # Si NO es administrador, y el modelo tiene campo delegacion, aplicamos el filtro
        es_admin = 'admin' in rol_nombre
        if not es_admin and hasattr(self.model, 'delegacion') and hasattr(user, 'delegacion') and user.delegacion:
            qs = qs.filter(delegacion=user.delegacion)
            
        return qs

    def serialize_instance(self, instance):
        """Convierte una instancia del modelo a diccionario JSON."""
        data = {"id": instance.pk}
        for field in self.fields:
            if hasattr(instance, field):
                val = getattr(instance, field)
                if hasattr(val, "pk"):
                    data[field] = val.pk
                else:
                    data[field] = val
        return data

    def filter_queryset(self, qs):
        """Aplica filtros estándar: búsqueda libre y estado."""
        search_query = self.request.GET.get("search", "").strip()
        if search_query and self.search_fields:
            q_filter = Q()
            for field in self.search_fields:
                q_filter |= Q(**{f"{field}__icontains": search_query})
            qs = qs.filter(q_filter)

        estado_filter = self.request.GET.get("estado", "activos").lower()
        if hasattr(self.model, self.soft_delete_field):
            if estado_filter == "activos":
                qs = qs.filter(**{self.soft_delete_field: True})
            elif estado_filter == "inactivos":
                qs = qs.filter(**{self.soft_delete_field: False})

        ordering = self.request.GET.get("ordering")
        if ordering:
            qs = qs.order_by(ordering)
        elif self.ordering:
            qs = qs.order_by(*self.ordering)

        return qs

    def get(self, request, pk=None, action=None, *args, **kwargs):
        """Maneja listado paginado, detalle o exportación a Excel."""
        if action == "export":
            # Extra: Verificar rol para exportar (Opcional, según reglas de negocio)
            return self.export(request)
        if pk is not None:
            return self.retrieve(request, pk)
        return self.list(request)

    def export(self, request):
        """Exporta los registros filtrados a formato XLSX nativo compatible con Excel (Tarea T12)."""
        qs = self.filter_queryset(self.get_queryset())
        model_name = self.model._meta.model_name
        filename = f"{model_name}_export.xlsx"

        # Crear el libro de Excel y la hoja activa
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = model_name.capitalize()

        field_labels = {
            "codigo": "Código",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "estado": "Estado",
            "direccion": "Dirección",
            "comuna": "Comuna"
        }
        
        # Generar cabeceras basadas en los campos autorizados (self.fields)
        headers = ["ID"] + [field_labels.get(f, f.replace("_", " ").title()) for f in self.fields]
        ws.append(headers)

        # Poblar filas completas ignorando la paginación
        for item in qs:
            row = [item.pk]
            for f in self.fields:
                val = getattr(item, f, "")
                if isinstance(val, bool):
                    val = "Activo" if val else "Inactivo"
                row.append(str(val) if val is not None else "")
            ws.append(row)

        # Preparar la respuesta HTTP para la descarga del archivo Excel
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        
        return response

    def list(self, request):
        qs = self.filter_queryset(self.get_queryset())
        
        try:
            page_size = int(request.GET.get("page_size", self.default_page_size))
            page_size = max(1, min(page_size, self.max_page_size))
        except ValueError:
            page_size = self.default_page_size

        paginator = Paginator(qs, page_size)
        page_num = request.GET.get("page", 1)

        try:
            page_obj = paginator.page(page_num)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        results = [self.serialize_instance(obj) for obj in page_obj]

        return JsonResponse({
            "success": True,
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "results": results
        }, status=200)

    def retrieve(self, request, pk):
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return api_error(
                code="NOT_FOUND",
                message=f"El registro con ID {pk} no existe o no tiene permisos para verlo.",
                status=404
            )
        return api_success(data=self.serialize_instance(instance))

    def validate_payload(self, data, instance=None):
        errors = {}
        for field in self.fields:
            model_field = self.model._meta.get_field(field)
            if not model_field.blank and not model_field.null:
                if field not in data or data[field] is None or data[field] == "":
                    if instance is None or field in data:
                        errors[field] = ["Este campo es obligatorio."]
        return errors

    def post(self, request, pk=None, action=None, *args, **kwargs):
        if action == "toggle-estado" and pk is not None:
            return self.toggle_estado(request, pk)

        data = request.json_data
        errors = self.validate_payload(data)
        if errors:
            return api_error(
                code="VALIDATION_ERROR",
                message="Error de validación en los datos enviados.",
                details=errors,
                status=400
            )

        try:
            instance = self.model()
            for field in self.fields:
                if field in data:
                    setattr(instance, field, data[field])
            
            # Autocompletar la delegación si el modelo lo requiere y el usuario la tiene
            if hasattr(instance, 'delegacion') and hasattr(request.user, 'delegacion') and request.user.delegacion:
                # Si no mandaron delegacion explícita o si NO es admin, forzamos la suya.
                rol_nombre = getattr(request.user.rol, 'nombre', '').lower() if hasattr(request.user, 'rol') and request.user.rol else ''
                if 'delegacion' not in data or 'admin' not in rol_nombre:
                    instance.delegacion = request.user.delegacion

            instance.full_clean()
            instance.save()
            return api_success(
                data=self.serialize_instance(instance),
                message="Registro creado exitosamente.",
                status=201
            )
        except IntegrityError as exc:
            return api_error(
                code="DUPLICATE_ERROR",
                message="Ya existe un registro con los mismos valores únicos.",
                details={"error": [str(exc)]},
                status=409
            )
        except ValidationError as exc:
            return api_error(
                code="VALIDATION_ERROR",
                message="Error de validación del modelo.",
                details=exc.message_dict if hasattr(exc, "message_dict") else {"error": exc.messages},
                status=400
            )

    def put(self, request, pk=None, *args, **kwargs):
        return self.update(request, pk, partial=False)

    def patch(self, request, pk=None, *args, **kwargs):
        return self.update(request, pk, partial=True)

    def update(self, request, pk, partial=True):
        try:
            # get_queryset() ya filtra por delegación, así que si intentan modificar algo ajeno, dará Error 404
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return api_error(code="NOT_FOUND", message=f"El registro con ID {pk} no existe o no tiene permisos para editarlo.", status=404)

        data = request.json_data
        
        # Evitar que se edite la delegación y se "robe" un registro a otro contexto
        if 'delegacion' in data:
            rol_nombre = getattr(request.user.rol, 'nombre', '').lower() if hasattr(request.user, 'rol') and request.user.rol else ''
            if 'admin' not in rol_nombre:
                data.pop('delegacion') # Quitamos el intento de cambio malicioso

        errors = self.validate_payload(data, instance=instance) if not partial else {}
        if errors:
            return api_error(
                code="VALIDATION_ERROR",
                message="Error de validación en los datos enviados.",
                details=errors,
                status=400
            )

        try:
            for field in self.fields:
                if field in data:
                    setattr(instance, field, data[field])
            instance.full_clean()
            instance.save()
            return api_success(
                data=self.serialize_instance(instance),
                message="Registro actualizado exitosamente."
            )
        except IntegrityError as exc:
            return api_error(
                code="DUPLICATE_ERROR",
                message="Conflicto de clave única al actualizar.",
                details={"error": [str(exc)]},
                status=409
            )
        except ValidationError as exc:
            return api_error(
                code="VALIDATION_ERROR",
                message="Error de validación del modelo.",
                details=exc.message_dict if hasattr(exc, "message_dict") else {"error": exc.messages},
                status=400
            )

    def delete(self, request, pk=None, *args, **kwargs):
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return api_error(code="NOT_FOUND", message=f"El registro con ID {pk} no existe o no tiene permisos para eliminarlo.", status=404)

        if hasattr(instance, self.soft_delete_field):
            setattr(instance, self.soft_delete_field, False)
            instance.save()
            return api_success(
                data={"id": instance.pk, self.soft_delete_field: False},
                message="Registro desactivado exitosamente."
            )
        else:
            instance.delete()
            return api_success(message="Registro eliminado exitosamente.")

    def toggle_estado(self, request, pk):
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return api_error(code="NOT_FOUND", message=f"El registro con ID {pk} no existe o no tiene permisos.", status=404)

        if hasattr(instance, self.soft_delete_field):
            nuevo_estado = not getattr(instance, self.soft_delete_field)
            setattr(instance, self.soft_delete_field, nuevo_estado)
            instance.save()
            estado_txt = "activado" if nuevo_estado else "desactivado"
            return api_success(
                data={"id": instance.pk, self.soft_delete_field: nuevo_estado},
                message=f"Registro {estado_txt} exitosamente."
            )
        return api_error(code="BAD_REQUEST", message="El modelo no soporta cambio de estado.")