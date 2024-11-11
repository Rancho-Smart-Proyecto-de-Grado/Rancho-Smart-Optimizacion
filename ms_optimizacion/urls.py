from django.urls import path
from . import views

urlpatterns = [
     path('optimizar_cruce/', views.optimizar_cruce, name='optimizar_cruce'),
]
