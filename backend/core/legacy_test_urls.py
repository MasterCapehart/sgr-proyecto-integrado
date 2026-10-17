"""Rutas del contrato anterior, exclusivamente para regresiones históricas."""
from django.urls import path, include
urlpatterns = [path("api/", include("core.legacy_api_urls"))]
