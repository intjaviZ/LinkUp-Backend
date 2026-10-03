# LinkUp Backend

Backend de LinkUp construido con Django y Django REST Framework. El proyecto usa PostgreSQL, autenticación JWT y configuración local mediante variables de entorno.

## Requisitos

- Python 3.12 o superior.
- PostgreSQL en ejecución y una base de datos creada para el proyecto.
- Git.

## Preparar el entorno local

Ejecuta estos pasos desde la carpeta `backend`:

1. Clona el repositorio y entra en la carpeta del backend:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <REPOSITORIO>/backend
   ```

   Si el repositorio clonado ya corresponde a esta carpeta, omite `cd <REPOSITORIO>/backend`.

2. Crea y activa un entorno virtual.

   **Windows PowerShell**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Crea tu archivo local de variables de entorno a partir de la plantilla.

   **Windows PowerShell**

   ```powershell
   Copy-Item .env.example .env
   ```

   **macOS / Linux**

   ```bash
   cp .env.example .env
   ```

5. Crea una base de datos y un usuario en PostgreSQL. Configura en `.env` las credenciales correspondientes. La plantilla incluye estas variables:

   | Variable | Descripción |
   | --- | --- |
   | `SECRET_KEY` | Clave secreta de Django; reemplaza el valor de ejemplo por una clave aleatoria local. |
   | `DEBUG` | Modo de depuración (`True` para desarrollo local). |
   | `ALLOWED_HOSTS` | Hosts permitidos, separados por comas. |
   | `DB_NAME` | Nombre de la base de datos PostgreSQL. |
   | `DB_USER` | Usuario de PostgreSQL. |
   | `DB_PASSWORD` | Contraseña de ese usuario. |
   | `DB_HOST` | Host del servidor PostgreSQL (por defecto, `localhost`). |
   | `DB_PORT` | Puerto de PostgreSQL (por defecto, `5432`). |
   | `CORS_ALLOWED_ORIGINS` | Orígenes permitidos para el frontend, separados por comas. |

   `.env` es local y no debe subirse al repositorio. Comparte los cambios de configuración actualizando `.env.example` sin incluir credenciales reales.

6. Aplica las migraciones y comprueba la configuración:

   ```bash
   python manage.py migrate
   python manage.py check
   ```

7. Inicia el servidor local:

   ```bash
   python manage.py runserver
   ```

   El backend estará disponible en <http://127.0.0.1:8000/>.

## Comandos útiles

Crear un usuario administrador para el panel de Django:

```bash
python manage.py createsuperuser
```

Ejecutar las pruebas:

```bash
python manage.py test
```

Comprobar cambios en los modelos y crear migraciones cuando corresponda:

```bash
python manage.py makemigrations
python manage.py migrate
```

Las migraciones existentes deben mantenerse en el control de versiones; no se excluyen en `.gitignore`.

## Rutas disponibles

- `/admin/`: panel administrativo de Django.
- `/api/docs/`: documentación Swagger generada con drf-spectacular.
- `/api/schema/`: esquema OpenAPI.

Las rutas de las aplicaciones todavía no están incluidas en `config/urls.py`; por ahora, la documentación no representa endpoints de negocio publicados.

## Estructura principal

- `config/`: configuración, URLs y puntos de entrada ASGI/WSGI.
- `usuarios/`: usuario personalizado con inicio de sesión basado en correo electrónico.
- `catalogo/`: planes estudiantiles y materias.
- `asesorias/`: modelos de asesorías, materias ofrecidas, habilidades, reseñas y cálculo de montos.
- `requirements.txt`: dependencias de Python.
- `.env.example`: plantilla de configuración local sin secretos.

## Tecnologías

Django 6.1, Django REST Framework, PostgreSQL, Simple JWT, django-filter, django-cors-headers y drf-spectacular.

## Notas de desarrollo

- No compartas ni confirmes archivos `.env` con credenciales reales.
- No uses `DEBUG=True` ni claves locales en un despliegue.
- Las pruebas están configuradas con Django, pero actualmente no hay casos de prueba implementados.
