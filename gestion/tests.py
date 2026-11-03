import re
from datetime import timedelta
from django.test import TestCase,Client
from django.contrib.auth.models import User,Group
from django.core.management import call_command
from django.utils import timezone
from django.core import mail
from cine.models import Genero,Pelicula
from noticias.models import Categoria,Noticia
from .models import Funcion,Reserva
class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('configurar_roles')
        cls.users={}
        for role in ['Administrador','Supervisor','Administrativo']:
            u=User.objects.create_user(role,role+'@example.com','Clave239Segura!')
            u.groups.add(Group.objects.get(name=role)); cls.users[role]=u
        cls.genero=Genero.objects.create(nombre='Drama')
        cls.pelicula=Pelicula.objects.create(titulo='Prueba',director='Director',genero=cls.genero,anio=2026,calificacion=8,sinopsis='Texto')
        cls.categoria=Categoria.objects.create(nombre='Tecnologia')
        cls.noticia=Noticia.objects.create(titulo='Noticia',categoria=cls.categoria,fecha='2026-11-01',resumen='Resumen',contenido='Contenido')
        cls.funcion=Funcion.objects.create(pelicula=cls.pelicula,fecha=timezone.now()+timedelta(days=2),cupos=3)
    def login(self,role='Administrador'):
        self.client.force_login(self.users[role])
    def test_paginas_y_roles(self):
        self.assertEqual(self.client.get('/noticias/').status_code,302)
        for role in self.users:
            self.login(role)
            self.assertContains(self.client.get('/'),'Panel '+role)
            for url in ['/noticias/','/cine/',f'/noticias/{self.noticia.pk}/',f'/cine/{self.pelicula.pk}/','/gestion/reservas/','/gestion/reservas/crear/']:
                self.assertEqual(self.client.get(url).status_code,200,url)
            self.assertEqual(self.client.get('/gestion/usuarios/').status_code,200 if role=='Administrador' else 403)
        self.assertEqual(self.client.post('/gestion/noticias/crear/',{}).status_code,403)
        self.assertEqual(self.client.get('/admin/').status_code,404)
    def test_crud_y_relaciones(self):
        self.login()
        for slug in ['categorias','generos','noticias','peliculas','funciones']:
            self.assertEqual(self.client.get('/gestion/'+slug+'/').status_code,200)
            self.assertEqual(self.client.get('/gestion/'+slug+'/crear/').status_code,200)
        for slug,model in [('categorias',Categoria),('generos',Genero)]:
            self.assertEqual(self.client.post('/gestion/'+slug+'/crear/',{'nombre':'Nueva','descripcion':'Texto'}).status_code,302)
            obj=model.objects.get(nombre='Nueva')
            self.assertContains(self.client.get('/gestion/'+slug+'/?q=Nueva'),'Nueva')
            self.assertEqual(self.client.post(f'/gestion/{slug}/{obj.pk}/modificar/',{'nombre':'Cambio','descripcion':'Texto'}).status_code,302)
            self.assertEqual(self.client.post(f'/gestion/{slug}/{obj.pk}/eliminar/').status_code,302)
            self.assertFalse(model.objects.filter(pk=obj.pk).exists())
        self.assertContains(self.client.post(f'/gestion/generos/{self.genero.pk}/eliminar/'),'existen registros relacionados')
    def test_reservas_cupos_cancelacion(self):
        self.login('Administrativo')
        url='/gestion/reservas/crear/'
        self.assertEqual(self.client.post(url,{'funcion':self.funcion.pk,'cantidad':2}).status_code,302)
        self.assertContains(self.client.post(url,{'funcion':self.funcion.pk,'cantidad':2}),'Solo quedan 1 cupos')
        self.assertEqual(Reserva.objects.count(),1)
        r=Reserva.objects.get()
        self.assertEqual(self.client.post(f'/gestion/reservas/{r.pk}/cancelar/').status_code,403)
        self.login('Supervisor')
        self.assertEqual(self.client.get(f'/gestion/reservas/{r.pk}/cancelar/').status_code,200)
        r.refresh_from_db(); self.assertFalse(r.cancelada)
        self.assertEqual(self.client.post(f'/gestion/reservas/{r.pk}/cancelar/').status_code,302)
        self.assertEqual(self.client.post(url,{'funcion':self.funcion.pk,'cantidad':3}).status_code,302)
    def test_validaciones(self):
        self.login()
        data={'titulo':'Mal','director':'Director','genero':self.genero.pk,'anio':2026,'calificacion':'11','sinopsis':'Texto'}
        self.assertContains(self.client.post('/gestion/peliculas/crear/',data),'entre 0 y 10')
        self.assertEqual(Pelicula.objects.count(),1)
        self.assertEqual(self.client.post('/gestion/reservas/crear/',{'funcion':self.funcion.pk,'cantidad':0}).status_code,200)
        self.assertEqual(Reserva.objects.count(),0)
    def test_usuarios(self):
        self.login()
        group=Group.objects.get(name='Administrativo')
        data={'username':'nuevo','email':'nuevo@example.com','grupo':group.pk,'password1':'Clave239Segura!','password2':'Clave239Segura!'}
        self.assertEqual(self.client.post('/gestion/usuarios/crear/',data).status_code,302)
        self.assertTrue(User.objects.get(username='nuevo').groups.filter(pk=group.pk).exists())
    def test_recuperacion(self):
        self.client.post('/cuentas/password_reset/',{'email':'Administrador@example.com'})
        self.assertEqual(len(mail.outbox),1)
        path=re.search(r'http://testserver([^\s]+)',mail.outbox[0].body).group(1)
        response=self.client.get(path)
        self.assertContains(self.client.get(response.url),'Nueva contraseña')
        self.assertEqual(self.client.post(response.url,{'new_password1':'Nueva239Segura!','new_password2':'Nueva239Segura!'}).status_code,302)
        self.assertTrue(self.client.login(username='Administrador',password='Nueva239Segura!'))
        self.assertContains(Client().get(path,follow=True),'venció')
    def test_csrf(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.users['Administrador'])
        self.assertEqual(client.post('/gestion/categorias/crear/',{'nombre':'Sin token'}).status_code,403)
