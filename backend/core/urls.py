from django.urls import path
from . import views

urlpatterns = [
    # Autenticación y Recuperación (T05, T06)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperacion/', views.solicitar_recuperacion, name='recuperacion'),

    # Endpoints TipoAtencion (T14)
    path('tipos-atencion/', views.TipoAtencionCRUDView.as_view(), name='tipo-atencion-list'),
    path('tipos-atencion/export/', views.TipoAtencionCRUDView.as_view(), {'action': 'export'}, name='tipo-atencion-export'),
    path('tipos-atencion/<int:pk>/', views.TipoAtencionCRUDView.as_view(), name='tipo-atencion-detail'),
    path('tipos-atencion/<int:pk>/toggle-estado/', views.TipoAtencionCRUDView.as_view(), {'action': 'toggle-estado'}, name='tipo-atencion-toggle'),

    # Endpoints Delegaciones (Referencia reutilizable para Matías T13)
    path('delegaciones/', views.DelegacionCRUDView.as_view(), name='delegacion-list'),
    path('delegaciones/export/', views.DelegacionCRUDView.as_view(), {'action': 'export'}, name='delegacion-export'),
    path('delegaciones/<int:pk>/', views.DelegacionCRUDView.as_view(), name='delegacion-detail'),
    path('delegaciones/<int:pk>/toggle-estado/', views.DelegacionCRUDView.as_view(), {'action': 'toggle-estado'}, name='delegacion-toggle'),

    # Endpoints SubAtencion (T15)
    path('subatenciones/', views.SubAtencionCRUDView.as_view(), name='subatencion-list'),
    path('subatenciones/export/', views.SubAtencionCRUDView.as_view(), {'action': 'export'}, name='subatencion-export'),
    path('subatenciones/<int:pk>/', views.SubAtencionCRUDView.as_view(), name='subatencion-detail'),
    path('subatenciones/<int:pk>/toggle-estado/', views.SubAtencionCRUDView.as_view(), {'action': 'toggle-estado'}, name='subatencion-toggle'),

    # Endpoints Ítems y Metas (T16)
    path('items-metas/', views.ItemMetaCRUDView.as_view(), name='item-meta-list'),
    path('items-metas/export/', views.ItemMetaCRUDView.as_view(), {'action': 'export'}, name='item-meta-export'),
    path('items-metas/<int:pk>/', views.ItemMetaCRUDView.as_view(), name='item-meta-detail'),
    path('items-metas/<int:pk>/toggle-estado/', views.ItemMetaCRUDView.as_view(), {'action': 'toggle-estado'}, name='item-meta-toggle'),
]
