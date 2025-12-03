import os
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from distutils.util import strtobool
from dotenv import load_dotenv

# ==========================================
# 1. ОСНОВНІ ШЛЯХИ ТА ЗМІННІ
# ==========================================
# Шлях до кореня проекту (де лежить manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Завантажуємо .env, якщо він є
load_dotenv(BASE_DIR / ".env")


def get_env_variable(name, default=None):
    return os.environ.get(name, default)


# ==========================================
# 2. БЕЗПЕКА (PRODUCTION)
# ==========================================
SECRET_KEY = get_env_variable("SECRET_KEY", "django-insecure-production-key-change-me")

# ВАЖЛИВО: Для продакшену False
DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "193.56.151.227", "sobes-prod-production.up.railway.app", "*"]

CSRF_TRUSTED_ORIGINS = [
    "http://193.56.151.227",
    "http://193.56.151.227:8000",
    "https://sobes-prod-production.up.railway.app",
]

# ==========================================
# 3. ДОДАТКИ (INSTALLED_APPS)
# ==========================================
INSTALLED_APPS = [
    'daphne',  # Має бути першим для WebSockets
    'channels',  # Другий для каналів
    'myapp.apps.MyappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Медіа та Статика
    'cloudinary_storage',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',
    'widget_tweaks',
    'wait_for_db_app',
    'django_celery_results',
    'cloudinary',
    'rest_framework',
    'drf_spectacular',
]

# ==========================================
# 4. MIDDLEWARE
# ==========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware', # ВИМКНЕНО: Nginx роздає статику сам
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sobes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myapp.context_processors.notifications_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'sobes.wsgi.application'
ASGI_APPLICATION = 'sobes.asgi.application'

# ==========================================
# 5. БАЗА ДАНИХ (PostgreSQL)
# ==========================================
database_url = os.environ.get('DATABASE_URL')

if database_url:
    DATABASES = {
        'default': dj_database_url.config(default=database_url, conn_max_age=600, ssl_require=False)
    }
else:
    # Фолбек на локальний PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'sobes',
            'USER': 'postgres',
            'PASSWORD': '12345678',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

# ==========================================
# 6. REDIS (Channels & Celery)
# ==========================================
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Channels (WebSockets)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# Celery
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_ALWAYS_EAGER = False

# ==========================================
# 7. СТАТИКА (STATIC FILES)
# ==========================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ВАЖЛИВО: Використовуємо стандартне сховище, щоб collectstatic зберіг файли у папку staticfiles,
# а Nginx міг їх звідти взяти. Cloudinary тут НЕ потрібен.
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ==========================================
# 8. МЕДІА (CLOUDINARY)
# ==========================================
# Налаштування Cloudinary (беремо з Env або хардкод, якщо треба)
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

# Якщо змінної немає, використовуємо явні ключі (твої дані)
if not CLOUDINARY_URL:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': 'dhact88gj',
        'API_KEY': '633531725433543',
        'API_SECRET': '1U31LQvhjYxWljoN8tBIx-i36hI'
    }
else:
    # Якщо є URL, бібліотека сама розбереться, але storage треба задати
    pass

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# 9. REST FRAMEWORK & API
# ==========================================
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 12,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Sobes API',
    'DESCRIPTION': 'API для OLX-like застосунку',
    'VERSION': '1.0.0',
}

# ==========================================
# 10. EMAIL SETTINGS
# ==========================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "Nazarshylo2005@gmail.com"
EMAIL_HOST_PASSWORD = "yyhd onkt maud cvdz"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==========================================
# 11. ІНШЕ
# ==========================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

CORS_ALLOW_ALL_ORIGINS = True  # Для тестів можна True, для проді краще налаштувати список