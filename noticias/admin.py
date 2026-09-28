from django.contrib import admin

from .models import Categoria, Noticia


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'total_noticias')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

    @admin.display(description='Noticias')
    def total_noticias(self, obj):
        return obj.noticias.count()


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha', 'destacado')
    list_filter = ('categoria', 'destacado', 'fecha')
    search_fields = ('titulo', 'resumen', 'contenido', 'categoria__nombre')
    date_hierarchy = 'fecha'
    list_editable = ('destacado',)
    list_select_related = ('categoria',)
    autocomplete_fields = ('categoria',)
    list_per_page = 20
    fieldsets = (
        ('Información principal', {
            'fields': ('titulo', 'categoria', 'fecha', 'destacado')
        }),
        ('Contenido', {
            'fields': ('resumen', 'contenido', 'imagen')
        }),
    )
