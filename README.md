# Portal Web Modular — Evaluación Sumativa N°2

Proyecto Django que evoluciona el prototipo basado en archivos JSON (Evaluación N°1)
hacia una aplicación con **persistencia en base de datos relacional**, administración
mediante **Django Admin** y listados construidos con **Django ORM**.

## Descripción

El sistema está compuesto por dos aplicaciones independientes:

- **Noticias:** gestión de noticias tecnológicas agrupadas por categoría.
- **Cine:** gestión de una cartelera de películas agrupadas por género.

Cada módulo cuenta con vistas de listado (obtenidas desde la base de datos mediante el
ORM) y vistas de detalle, e incorpora botones de acción (Agregar, Modificar, Eliminar,
Buscar) preparados para la siguiente evaluación.

## Arquitectura

```
Proyecto/
├── manage.py
├── requirements.txt
├── .env.example            # Plantilla de variables de entorno
├── .gitignore
├── mi_proyecto/            # Configuración del proyecto
│   ├── settings.py         # Config cargada desde .env (python-decouple)
│   ├── urls.py
│   └── ...
├── noticias/               # Aplicación de Noticias
│   ├── models.py           # Categoria, Noticia
│   ├── admin.py            # Registro en Django Admin
│   ├── views.py            # Consultas ORM
│   ├── urls.py
│   ├── migrations/
│   └── management/commands/cargar_noticias.py
├── cine/                   # Aplicación de Cine
│   ├── models.py           # Genero, Pelicula
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── management/commands/cargar_peliculas.py
├── templates/base.html     # Plantilla base con Bootstrap local
├── static/                 # CSS, JS e imágenes
└── data/                   # JSON originales (fuente de la migración)
```

## Modelo de Datos

| Entidad    | Campos                                                                              | Relación                          |
| :--------- | :---------------------------------------------------------------------------------- | :-------------------------------- |
| `Categoria`| nombre, descripcion                                                                 | 1 → N `Noticia`                   |
| `Noticia`  | titulo, categoria (FK), fecha, resumen, contenido, destacado, imagen                | N → 1 `Categoria` (`PROTECT`)     |
| `Genero`   | nombre, descripcion                                                                 | 1 → N `Pelicula`                  |
| `Pelicula` | titulo, director, genero (FK), anio, calificacion, sinopsis, estreno, imagen        | N → 1 `Genero` (`PROTECT`)        |

Todas las entidades están registradas en Django Admin con listados, búsqueda y filtros.

## Puesta en marcha 

´´´bash
# 1. Clonar el repositorio
git clone URL_DEL_REPOSITORIO
cd Proyecto

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env            # y editar los valores

# 5. Aplicar migraciones y crear superusuario
python manage.py migrate
python manage.py createsuperuser

# 6. Cargar los datos desde los JSON hacia la base de datos
python manage.py cargar_noticias
python manage.py cargar_peliculas

# 7. Ejecutar el servidor
python manage.py runserver
```

- Front-end: http://127.0.0.1:8000/noticias/ y http://127.0.0.1:8000/cine/
- Django Admin: http://127.0.0.1:8000/admin/

## Variables de entorno

Toda la configuración sensible vive en el archivo `.env` (no versionado):

| Variable              | Descripción                                            |
| :-------------------- | :----------------------------------------------------- |
| `SECRET_KEY`          | Clave secreta de Django                                |
| `DEBUG`               | `True` en desarrollo, `False` en producción            |
| `ALLOWED_HOSTS`       | Hosts permitidos (separados por coma)                  |
| `CSRF_TRUSTED_ORIGINS`| Dominios/IPs de confianza para CSRF                    |
| `DB_ENGINE`           | `sqlite` (local) o `mysql` (EC2 / producción)          |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexión MySQL |

## Despliegue en AWS EC2 (resumen)

```bash
sudo apt update
sudo apt install python3-venv python3-dev default-libmysqlclient-dev build-essential git -y

git clone URL_DEL_REPOSITORIO
cd Proyecto
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar .env con DB_ENGINE=mysql y las credenciales correspondientes
cp .env.example .env

python manage.py migrate
python manage.py cargar_noticias
python manage.py cargar_peliculas
python manage.py collectstatic --noinput
python manage.py createsuperuser

python manage.py runserver 0.0.0.0:8000
```

> En producción se recomienda `DEBUG=False`, un servidor como Gunicorn detrás de Nginx
> y una base de datos MySQL/MariaDB administrable desde phpMyAdmin.
