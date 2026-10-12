import json
from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import IntegrityError


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


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class BaseCRUDView(View):
    """
    Clase base reusable para vistas CRUD según el Patrón Común de API (Tarea T04).
    
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
        """Manejo centralizado de parseo de JSON en métodos que envían cuerpo."""
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
        """Retorna el queryset base para el modelo."""
        if self.model is None:
            raise NotImplementedError("Debe definir 'model' en la vista CRUD.")
        return self.model.objects.all()

    def serialize_instance(self, instance):
        """Convierte una instancia del modelo a diccionario JSON."""
        data = {"id": instance.pk}
        for field in self.fields:
            if hasattr(instance, field):
                val = getattr(instance, field)
                # Si es modelo relacionado, obtener ID
                if hasattr(val, "pk"):
                    data[field] = val.pk
                else:
                    data[field] = val
        return data

    def filter_queryset(self, qs):
        """Aplica filtros estándar: búsqueda libre y estado."""
        # 1. Búsqueda libre
        search_query = self.request.GET.get("search", "").strip()
        if search_query and self.search_fields:
            q_filter = Q()
            for field in self.search_fields:
                q_filter |= Q(**{f"{field}__icontains": search_query})
            qs = qs.filter(q_filter)

        # 2. Filtro por estado
        estado_filter = self.request.GET.get("estado", "activos").lower()
        if hasattr(self.model, self.soft_delete_field):
            if estado_filter == "activos":
                qs = qs.filter(**{self.soft_delete_field: True})
            elif estado_filter == "inactivos":
                qs = qs.filter(**{self.soft_delete_field: False})
            # Si es 'todos', no se filtra por estado

        # 3. Ordenamiento
        ordering = self.request.GET.get("ordering")
        if ordering:
            qs = qs.order_by(ordering)
        elif self.ordering:
            qs = qs.order_by(*self.ordering)

        return qs

    def get(self, request, pk=None, action=None, *args, **kwargs):
        """Maneja listado paginado, detalle o exportación a Excel/CSV."""
        if action == "export":
            return self.export(request)
        if pk is not None:
            return self.retrieve(request, pk)
        return self.list(request)

    def export(self, request):
        """Exporta los registros filtrados a formato CSV compatible directamente con Excel."""
        import csv
        from django.http import HttpResponse

        qs = self.filter_queryset(self.get_queryset())
        filename = f"{self.model._meta.model_name}_export.csv"

        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        field_labels = {
            "codigo": "Código",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "estado": "Estado",
            "direccion": "Dirección",
            "comuna": "Comuna"
        }
        headers = ["ID"] + [field_labels.get(f, f.replace("_", " ").title()) for f in self.fields]
        writer.writerow(headers)

        for item in qs:
            row = [item.pk]
            for f in self.fields:
                val = getattr(item, f, "")
                if isinstance(val, bool):
                    val = "Activo" if val else "Inactivo"
                row.append(str(val) if val is not None else "")
            writer.writerow(row)

        return response

    def list(self, request):
        """Retorna listado paginado según el contrato común."""
        qs = self.filter_queryset(self.get_queryset())
        
        # Paginación
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
        """Retorna el detalle de un registro específico."""
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return api_error(
                code="NOT_FOUND",
                message=f"El registro con ID {pk} no existe.",
                status=404
            )
        return api_success(data=self.serialize_instance(instance))

    def validate_payload(self, data, instance=None):
        """Valida campos requeridos y formatos. Puede ser sobrescrito."""
        errors = {}
        for field in self.fields:
            # Si el campo es obligatorio en el modelo y no está presente
            model_field = self.model._meta.get_field(field)
            if not model_field.blank and not model_field.null:
                if field not in data or data[field] is None or data[field] == "":
                    if instance is None or field in data:
                        errors[field] = ["Este campo es obligatorio."]
        return errors

    def post(self, request, pk=None, action=None, *args, **kwargs):
        """Crea un nuevo registro o ejecuta una acción personalizada como toggle-estado."""
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
        """Actualización total de un registro."""
        return self.update(request, pk, partial=False)

    def patch(self, request, pk=None, *args, **kwargs):
        """Actualización parcial de un registro."""
        return self.update(request, pk, partial=True)

    def update(self, request, pk, partial=True):
        """Actualiza un registro existente."""
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return api_error(code="NOT_FOUND", message=f"El registro con ID {pk} no existe.", status=404)

        data = request.json_data
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
        """Desactiva lógicamente el registro para conservar trazabilidad histórica."""
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return api_error(code="NOT_FOUND", message=f"El registro con ID {pk} no existe.", status=404)

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
        """Alterna el estado activo/inactivo de un registro."""
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return api_error(code="NOT_FOUND", message=f"El registro con ID {pk} no existe.", status=404)

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
