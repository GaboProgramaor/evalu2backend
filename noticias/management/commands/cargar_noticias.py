import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from noticias.models import Categoria, Noticia


class Command(BaseCommand):
    help = 'Migra las noticias almacenadas en data/noticias.json hacia la base de datos.'

    def handle(self, *args, **options):
        ruta = Path(settings.BASE_DIR) / 'data' / 'noticias.json'
        with open(ruta, encoding='utf-8') as archivo:
            datos = json.load(archivo)

        nuevas = 0
        for item in datos:
            categoria, _ = Categoria.objects.get_or_create(
                nombre=item['categoria'],
                defaults={'descripcion': f'Categoría {item["categoria"]}'},
            )
            _, creada = Noticia.objects.update_or_create(
                titulo=item['titulo'],
                defaults={
                    'categoria': categoria,
                    'fecha': parse_date(item['fecha']),
                    'resumen': item['resumen'],
                    'contenido': item['contenido'],
                    'destacado': item['destacado'],
                    'imagen': item['imagen'],
                },
            )
            nuevas += int(creada)

        self.stdout.write(
            self.style.SUCCESS(
                f'Noticias procesadas: {len(datos)} | nuevas: {nuevas}'
            )
        )
