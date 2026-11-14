from django.urls import path
from . import letter_api as api
urlpatterns=[path('cartas/',api.records),path('cartas/opciones/',api.options),path('cartas/<int:pk>/',api.records),path('cartas/<int:pk>/estado/',api.records,{'action':'estado'}),path('cartas/<int:pk>/reabrir/',api.records,{'action':'reabrir'}),path('cartas/<int:pk>/documentos/',api.documents),path('cartas/<int:pk>/documentos/<int:document_id>/',api.documents)]
