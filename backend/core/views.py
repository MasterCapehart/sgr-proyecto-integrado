from .models import TipoAtencion, Delegacion
from .api import BaseCRUDView


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
