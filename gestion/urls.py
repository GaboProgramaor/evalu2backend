from django.urls import path
from . import views
app_name='gestion'
urlpatterns=[
 path('reservas/',views.reservas,name='reservas'),
 path('reservas/crear/',views.reservar,name='reservar'),
 path('reservas/<int:pk>/cancelar/',views.cancelar,name='cancelar'),
 path('usuarios/',views.usuarios,name='usuarios'),
 path('usuarios/crear/',views.usuario_form,name='usuario_crear'),
 path('usuarios/<int:pk>/modificar/',views.usuario_form,name='usuario_modificar'),
 path('<slug:slug>/',views.entidad,name='lista'),
 path('<slug:slug>/crear/',views.entidad,{'accion':'add'},name='crear'),
 path('<slug:slug>/<int:pk>/modificar/',views.entidad,{'accion':'change'},name='modificar'),
 path('<slug:slug>/<int:pk>/eliminar/',views.entidad,{'accion':'delete'},name='eliminar'),
]
