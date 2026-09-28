from django.db import models


class Categoria(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Noticia(models.Model):
    titulo = models.CharField('Título', max_length=200)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='noticias',
        verbose_name='Categoría',
    )
    fecha = models.DateField('Fecha de publicación')
    resumen = models.TextField('Resumen')
    contenido = models.TextField('Contenido')
    destacado = models.BooleanField('Destacado', default=False)
    imagen = models.CharField('Imagen', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'
        ordering = ['-fecha', 'titulo']

    def __str__(self):
        return self.titulo
