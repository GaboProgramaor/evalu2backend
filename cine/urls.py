from django.urls import path

from . import views

app_name = 'cine'

urlpatterns = [
    path('', views.cartelera, name='cartelera'),
    path('<int:pk>/', views.detalle_pelicula, name='detalle_pelicula'),
]
