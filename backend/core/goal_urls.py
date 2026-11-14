from django.urls import path
from .goal_api import assignments
urlpatterns=[path('',assignments),path('<int:pk>/',assignments)]
