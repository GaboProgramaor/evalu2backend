from django.urls import path,include
from gestion.views import inicio
urlpatterns=[path('',inicio,name='inicio'),path('cuentas/',include('django.contrib.auth.urls')),path('gestion/',include('gestion.urls')),path('noticias/',include('noticias.urls')),path('cine/',include('cine.urls'))]
