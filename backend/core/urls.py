from django.urls import path
from .views import TipoAtencionCRUDView, DelegacionCRUDView

urlpatterns = [
    # Endpoints TipoAtencion (Ejemplo conectado T04 / T14)
    path('tipos-atencion/', TipoAtencionCRUDView.as_view(), name='tipo-atencion-list'),
    path('tipos-atencion/<int:pk>/', TipoAtencionCRUDView.as_view(), name='tipo-atencion-detail'),
    path('tipos-atencion/<int:pk>/toggle-estado/', TipoAtencionCRUDView.as_view(), {'action': 'toggle-estado'}, name='tipo-atencion-toggle'),

    # Endpoints Delegaciones (Referencia reutilizable para Matías T13)
    path('delegaciones/', DelegacionCRUDView.as_view(), name='delegacion-list'),
    path('delegaciones/<int:pk>/', DelegacionCRUDView.as_view(), name='delegacion-detail'),
    path('delegaciones/<int:pk>/toggle-estado/', DelegacionCRUDView.as_view(), {'action': 'toggle-estado'}, name='delegacion-toggle'),
]
