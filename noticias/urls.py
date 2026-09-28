from django.urls import path

from . import views

app_name = 'noticias'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('<int:pk>/', views.detalle, name='detalle'),
]
