from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Genero, Pelicula


def cartelera(request):
    """Listado de películas obtenido mediante consultas del ORM."""
    query = request.GET.get('q', '').strip()

    peliculas = Pelicula.objects.select_related('genero')
    if query:
        peliculas = peliculas.filter(
            Q(titulo__icontains=query)
            | Q(director__icontains=query)
            | Q(sinopsis__icontains=query)
            | Q(genero__nombre__icontains=query)
        )

    contexto = {
        'peliculas': peliculas,
        'generos': Genero.objects.all(),
        'query': query,
    }
    return render(request, 'cine/cartelera.html', contexto)


def detalle_pelicula(request, pk):
    """Ficha de una película específica."""
    pelicula = get_object_or_404(
        Pelicula.objects.select_related('genero'), pk=pk
    )
    return render(request, 'cine/detalle_pelicula.html', {'pelicula': pelicula})
