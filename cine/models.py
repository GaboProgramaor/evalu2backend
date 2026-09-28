from django.db import models


class Genero(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    titulo = models.CharField('Título', max_length=200)
    director = models.CharField('Director', max_length=150)
    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT,
        related_name='peliculas',
        verbose_name='Género',
    )
    anio = models.PositiveIntegerField('Año')
    calificacion = models.DecimalField('Calificación', max_digits=3, decimal_places=1)
    sinopsis = models.TextField('Sinopsis')
    estreno = models.BooleanField('Estreno', default=False)
    imagen = models.CharField('Imagen', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Película'
        verbose_name_plural = 'Películas'
        ordering = ['-anio', 'titulo']

    def __str__(self):
        return f'{self.titulo} ({self.anio})'
