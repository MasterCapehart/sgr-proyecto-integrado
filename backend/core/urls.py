from django.urls import path
from . import views

urlpatterns = [
    # Autenticación y Recuperación (T05, T06)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperacion/', views.solicitar_recuperacion, name='recuperacion'),
    path('validar-recuperacion/', views.validar_y_cambiar_password, name='validar-recuperacion'),

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

    # Endpoints Registro de Atención Ciudadana (T17 / T18)
    path('atenciones/contexto/', views.AtencionContextoView.as_view(), name='atencion-contexto'),
    path('atenciones/', views.AtencionCRUDView.as_view(), name='atencion-list'),
    path('atenciones/export/', views.AtencionCRUDView.as_view(), {'action': 'export'}, name='atencion-export'),
    path('atenciones/<int:pk>/', views.AtencionCRUDView.as_view(), name='atencion-detail'),
    path('atenciones/<int:pk>/toggle-estado/', views.AtencionCRUDView.as_view(), {'action': 'toggle-estado'}, name='atencion-toggle'),

    # Endpoints Contexto Global y Cambio de Ámbito Territorial (T19)
    path('contexto/', views.ContextoView.as_view(), name='contexto-global'),
    path('contexto/cambiar-delegacion/', views.CambiarDelegacionView.as_view(), name='cambiar-delegacion'),
]


