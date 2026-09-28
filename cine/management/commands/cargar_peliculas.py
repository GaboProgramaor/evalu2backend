import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from cine.models import Genero, Pelicula


class Command(BaseCommand):
    help = 'Migra las películas almacenadas en data/peliculas.json hacia la base de datos.'

    def handle(self, *args, **options):
        ruta = Path(settings.BASE_DIR) / 'data' / 'peliculas.json'
        with open(ruta, encoding='utf-8') as archivo:
            datos = json.load(archivo)

        nuevas = 0
        for item in datos:
            genero, _ = Genero.objects.get_or_create(
                nombre=item['genero'],
                defaults={'descripcion': f'Género {item["genero"]}'},
            )
            _, creada = Pelicula.objects.update_or_create(
                titulo=item['titulo'],
                defaults={
                    'director': item['director'],
                    'genero': genero,
                    'anio': item['anio'],
                    'calificacion': Decimal(str(item['calificacion'])),
                    'sinopsis': item['sinopsis'],
                    'estreno': item['estreno'],
                    'imagen': item['imagen'],
                },
            )
            nuevas += int(creada)

        self.stdout.write(
            self.style.SUCCESS(
                f'Películas procesadas: {len(datos)} | nuevas: {nuevas}'
            )
        )
