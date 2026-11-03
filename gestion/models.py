from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from cine.models import Pelicula
class Funcion(models.Model):
    pelicula=models.ForeignKey(Pelicula,on_delete=models.PROTECT,related_name='funciones')
    fecha=models.DateTimeField()
    cupos=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    class Meta:
        ordering=['fecha','pk']
        verbose_name='función'
    def __str__(self):
        return f'{self.pelicula} — {self.fecha:%d/%m/%Y %H:%M}'
class Reserva(models.Model):
    funcion=models.ForeignKey(Funcion,on_delete=models.PROTECT,related_name='reservas')
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    cantidad=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    creada=models.DateTimeField(auto_now_add=True)
    cancelada=models.BooleanField(default=False)
    class Meta:
        ordering=['-creada']
    def __str__(self):
        return f'Reserva {self.pk}: {self.funcion}'
