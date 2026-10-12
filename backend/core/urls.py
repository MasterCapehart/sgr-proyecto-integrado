from django.urls import path
from . import views

urlpatterns = [
    # Autenticación (T05)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Endpoints TipoAtencion (Ejemplo conectado T04 / T14)
    path('tipos-atencion/', views.TipoAtencionCRUDView.as_view(), name='tipo-atencion-list'),
    path('tipos-atencion/<int:pk>/', views.TipoAtencionCRUDView.as_view(), name='tipo-atencion-detail'),
    path('tipos-atencion/<int:pk>/toggle-estado/', views.TipoAtencionCRUDView.as_view(), {'action': 'toggle-estado'}, name='tipo-atencion-toggle'),

    # Endpoints Delegaciones (Referencia reutilizable para Matías T13)
    path('delegaciones/', views.DelegacionCRUDView.as_view(), name='delegacion-list'),
    path('delegaciones/<int:pk>/', views.DelegacionCRUDView.as_view(), name='delegacion-detail'),
    path('delegaciones/<int:pk>/toggle-estado/', views.DelegacionCRUDView.as_view(), {'action': 'toggle-estado'}, name='delegacion-toggle'),
]
