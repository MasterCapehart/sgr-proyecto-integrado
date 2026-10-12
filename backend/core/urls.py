from django.urls import path
from . import views

urlpatterns = [
    # Tus endpoints de Autenticación y Recuperación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperacion/', views.solicitar_recuperacion, name='recuperacion'),
    
    # Endpoints TipoAtencion (De tus compañeros)
    path('tipos-atencion/', views.TipoAtencionCRUDView.as_view(), name='tipo-atencion-list'),
    path('tipos-atencion/<int:pk>/', views.TipoAtencionCRUDView.as_view(), name='tipo-atencion-detail'),
    path('tipos-atencion/<int:pk>/toggle-estado/', views.TipoAtencionCRUDView.as_view(), {'action': 'toggle-estado'}, name='tipo-atencion-toggle'),

    # Endpoints Delegaciones (De tus compañeros)
    path('delegaciones/', views.DelegacionCRUDView.as_view(), name='delegacion-list'),
    path('delegaciones/<int:pk>/', views.DelegacionCRUDView.as_view(), name='delegacion-detail'),
    path('delegaciones/<int:pk>/toggle-estado/', views.DelegacionCRUDView.as_view(), {'action': 'toggle-estado'}, name='delegacion-toggle'),
]