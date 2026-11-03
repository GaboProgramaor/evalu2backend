# Portal Web Modular — Evaluación Sumativa N°3

Proyecto Django que continúa la aplicación de la Evaluación N°2, con **persistencia en base de datos relacional**, gestión mediante **interfaces propias**, autenticación y permisos diferenciados.

## Descripción

El sistema está compuesto por los módulos originales:

- **Noticias:** gestión de noticias tecnológicas agrupadas por categoría.
- **Cine:** gestión de una cartelera de películas agrupadas por género.

La continuación incorpora el módulo **Gestión**, encargado de los dashboards, usuarios, perfiles, funciones de cine y reservas de entradas.

Los mantenedores de categorías, noticias, géneros, películas y funciones permiten agregar, buscar, listar, modificar y eliminar registros mediante Django Templates, formularios Django y Bootstrap local. La ruta de Django Admin está deshabilitada.

## Arquitectura

```
Proyecto/
├── manage.py
├── requirements.txt
├── .env.example            # Plantilla de variables de entorno
├── .gitignore
├── mi_proyecto/            # Configuración del proyecto
│   ├── settings.py         # Configuración desde .env con python-decouple
│   ├── urls.py
│   └── test_settings.py    # Base aislada para pruebas
├── noticias/               # Categoria, Noticia, listados y detalles
├── cine/                   # Genero, Pelicula y cartelera
├── gestion/                # Funciones, reservas, usuarios y perfiles
│   ├── models.py           # Funcion, Reserva
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── migrations/
│   └── management/commands/configurar_roles.py
├── templates/
│   ├── base.html           # Plantilla base con Bootstrap local
│   ├── gestion/            # Dashboards y formularios
│   └── registration/       # Login y recuperación de contraseña
├── static/                 # CSS, JS e imágenes
├── data/                   # JSON originales para carga de demostración
└── docs/                   # Informe técnico
```

## Modelo de Datos

| Entidad | Campos principales | Relación |
| :--- | :--- | :--- |
| `Categoria` | nombre, descripcion | 1 → N `Noticia` |
| `Noticia` | titulo, categoria, fecha, resumen, contenido, destacado, imagen | FK a `Categoria` |
| `Genero` | nombre, descripcion | 1 → N `Pelicula` |
| `Pelicula` | titulo, director, genero, anio, calificacion, sinopsis, estreno, imagen | FK a `Genero` |
| `Funcion` | pelicula, fecha, cupos | FK a `Pelicula` |
| `Reserva` | funcion, usuario, cantidad, creada, cancelada | FK a `Funcion` y `User` |

Las relaciones del dominio utilizan `PROTECT`. Los usuarios, grupos y permisos corresponden al sistema de autenticación de Django.

La reserva exige una cantidad positiva, una función futura y disponibilidad de cupos. El guardado utiliza `transaction.atomic` y `select_for_update` en MariaDB. La cancelación conserva el registro y libera disponibilidad. Esta operación no procesa pagos.

## Perfiles de usuario

| Operación | Administrador | Supervisor | Administrativo |
| :--- | :---: | :---: | :---: |
| Consultar contenidos y funciones | Sí | Sí | Sí |
| Crear y modificar mantenedores | Sí | Sí | No |
| Eliminar mantenedores | Sí | No | No |
| Registrar reservas | Sí | Sí | Sí |
| Cancelar reservas | Sí | Sí | No |
| Gestionar usuarios y perfiles | Sí | No | No |

Cada perfil dispone de un dashboard. Los permisos se comprueban en el servidor, además de condicionar las opciones visibles. El dashboard Administrativo muestra sus reservas recientes; el listado general permite consulta operacional.

## Puesta en marcha

```bash
# 1. Clonar el repositorio
git clone https://github.com/GaboProgramaor/evalu2backend.git
cd evalu2backend

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
# Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Windows: copy .env.example .env
# Configurar SECRET_KEY, DEBUG, ALLOWED_HOSTS y DB_ENGINE

# 5. Aplicar migraciones, configurar perfiles y crear superusuario
python manage.py migrate
python manage.py configurar_roles
python manage.py createsuperuser

# 6. Cargar datos de demostración en una instalación nueva
python manage.py cargar_noticias
python manage.py cargar_peliculas

# 7. Ejecutar el servidor
python manage.py runserver
```

- Panel de inicio: http://127.0.0.1:8000/
- Noticias: http://127.0.0.1:8000/noticias/
- Cine: http://127.0.0.1:8000/cine/
- Recuperación: http://127.0.0.1:8000/cuentas/password_reset/

Los módulos requieren autenticación. La creación de cuentas se realiza desde Usuarios, con un perfil autorizado. Los datos existentes deben respaldarse antes de ejecutar cargas de demostración.

## Variables de entorno

Toda la configuración sensible se mantiene en `.env`, excluido del repositorio:

| Variable | Descripción |
| :--- | :--- |
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `True` en desarrollo, `False` en producción |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma |
| `CSRF_TRUSTED_ORIGINS` | Orígenes de confianza para CSRF |
| `DB_ENGINE` | `sqlite` para desarrollo o `mysql` para EC2 |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexión MySQL/MariaDB |
| `EMAIL_BACKEND` | Backend de consola local o SMTP |
| `EMAIL_HOST`, `EMAIL_PORT` | Servidor y puerto de correo |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Cuenta y credencial SMTP |
| `EMAIL_USE_TLS` | Conexión SMTP mediante STARTTLS |
| `DEFAULT_FROM_EMAIL` | Dirección remitente |

Para Gmail se utilizan `smtp.gmail.com`, puerto `587`, `EMAIL_USE_TLS=True` y una contraseña de aplicación. La recuperación por correo se verificó en EC2. Los tokens vencen en una hora y se invalidan al cambiar la contraseña. El backend de consola no envía correos reales.

Las contraseñas, archivos .env, llaves PEM y enlaces activos de recuperación no se publican.

## Despliegue en AWS EC2

La aplicación está disponible en http://3.217.227.197/ y utiliza MariaDB, Apache y Gunicorn.

- Código: `/home/ubuntu/portal-eva3`.
- Servicio: `portal-eva3.service`, habilitado al inicio de la instancia.
- Gunicorn: dos workers en `127.0.0.1:8002`.
- Apache: proxy en el puerto 80 y estáticos en `/var/www/portal-static`.

```bash
# Actualización después de respaldar código, configuración y base
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py configurar_roles
python manage.py collectstatic --noinput
# Sincronizar staticfiles/ con /var/www/portal-static/
sudo systemctl restart portal-eva3

# Comprobaciones
sudo systemctl status portal-eva3 --no-pager
sudo apache2ctl configtest
```

Una instalación nueva requiere instalar y configurar Gunicorn, el servicio systemd y el proxy de Apache. La configuración .env del servidor y la base MariaDB se conservan durante las actualizaciones. HTTPS permanece pendiente; la URL actual utiliza HTTP. Si cambia la IP pública, deben actualizarse los hosts permitidos y la configuración web.

## Pruebas

```bash
python manage.py check
python manage.py test gestion --settings=mi_proyecto.test_settings
```

Las siete pruebas cubren autenticación y permisos, CRUD y búsqueda, relaciones protegidas, reservas y cupos, validaciones, usuarios, recuperación por token y CSRF. Se ejecutan con SQLite aislado; el entorno desplegado utiliza MariaDB.

## Documentación

El [informe técnico](docs/Informe_Evaluacion3.pdf) incluye la descripción del proyecto, seguridad, modelo de datos, capturas de interfaces, transacción y despliegue. Las evidencias de prompts y los anexos externos se completan por separado.
