from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db import transaction
class Command(BaseCommand):
    help='Crea o actualiza los tres perfiles sin crear usuarios ni contrasenas.'
    @transaction.atomic
    def handle(self,*args,**kwargs):
        for nombre in ['Administrador','Supervisor','Administrativo']:
            grupo,_=Group.objects.get_or_create(name=nombre)
            permisos=[]
            for perm in Permission.objects.select_related('content_type').all():
                app=perm.content_type.app_label
                model=perm.content_type.model
                action=perm.codename.split('_',1)[0]
                permitir=False
                if app in ['noticias','cine','gestion']:
                    permitir=nombre=='Administrador' or (nombre=='Supervisor' and action in ['view','add','change']) or (nombre=='Administrativo' and (action=='view' or (model in ['reserva'] and action=='add')))
                if nombre=='Administrador' and app=='auth' and model=='user' and action in ['view','add','change']:
                    permitir=True
                if permitir:
                    permisos.append(perm)
            grupo.permissions.set(permisos)
            self.stdout.write(self.style.SUCCESS(nombre+': '+str(len(permisos))+' permisos'))
