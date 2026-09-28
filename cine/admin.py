from django.contrib import admin

from .models import Genero, Pelicula


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'total_peliculas')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

    @admin.display(description='Películas')
    def total_peliculas(self, obj):
        return obj.peliculas.count()


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'director', 'genero', 'anio', 'calificacion', 'estreno')
    list_filter = ('genero', 'estreno', 'anio')
    search_fields = ('titulo', 'director', 'sinopsis', 'genero__nombre')
    list_editable = ('estreno',)
    list_select_related = ('genero',)
    autocomplete_fields = ('genero',)
    list_per_page = 20
    fieldsets = (
        ('Información principal', {
            'fields': ('titulo', 'director', 'genero', 'anio', 'calificacion', 'estreno')
        }),
        ('Detalle', {
            'fields': ('sinopsis', 'imagen')
        }),
    )
