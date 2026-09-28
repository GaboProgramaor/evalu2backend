from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Categoria, Noticia


def inicio(request):
    """Listado de noticias obtenido mediante consultas del ORM."""
    query = request.GET.get('q', '').strip()

    noticias = Noticia.objects.select_related('categoria')
    if query:
        noticias = noticias.filter(
            Q(titulo__icontains=query)
            | Q(resumen__icontains=query)
            | Q(contenido__icontains=query)
            | Q(categoria__nombre__icontains=query)
        )

    contexto = {
        'noticias': noticias,
        'categorias': Categoria.objects.all(),
        'query': query,
    }
    return render(request, 'noticias/inicio.html', contexto)


def detalle(request, pk):
    """Ficha de una noticia específica."""
    noticia = get_object_or_404(
        Noticia.objects.select_related('categoria'), pk=pk
    )
    return render(request, 'noticias/detalle.html', {'noticia': noticia})
