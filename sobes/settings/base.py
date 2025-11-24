from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
from distutils.util import strtobool
from dotenv import load_dotenv
import re
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Завантаження змінних
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


# ======== Helpers ========
def get_env_variable(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and val is None:
        raise ImproperlyConfigured(f"Environment variable '{name}' is required")
    return val


def bool_env(name, default=False):
    val = os.environ.get(name, str(default))
    try:
        return bool(strtobool(val))
    except Exception:
        return str(val).lower() in ("1", "true", "yes", "on")


# ======== Core ========
SECRET_KEY = get_env_variable("SECRET_KEY", "django-insecure-PLACEHOLDER")
DEBUG = bool_env("DEBUG", default=False)

ALLOWED_HOSTS = []
CORS_ALLOW_ALL_ORIGINS = bool_env("CORS_ALLOW_ALL_ORIGINS", default=False)

# ======== Apps ========
INSTALLED_APPS = [
    'daphne',
    'channels',
    'myapp.apps.MyappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # ВАЖЛИВО: cloudinary_storage має бути вище, ніж staticfiles
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

# ======== REST Framework ========
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

# ======== Middleware ========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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

ASGI_APPLICATION = 'sobes.asgi.application'

# ======== Static Files (WhiteNoise) ========
STATICFILES_DIRS = [
    '/app/static',
]

# 2. Куди collectstatic їх складе (це папка, звідки роздає WhiteNoise)
STATIC_ROOT = '/app/staticfiles'

# 3. WhiteNoise налаштування
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ======== Cloudinary / Media Configuration ========
# Спроба отримати довгий URL (наприклад, з Railway)
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

if CLOUDINARY_URL:
    try:
        # Парсимо URL вигляду cloudinary://API_KEY:API_SECRET@CLOUD_NAME
        raw_config = CLOUDINARY_URL.replace('cloudinary://', '')
        creds, cloud_name = raw_config.split('@')
        api_key, api_secret = creds.split(':')

        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': cloud_name,
            'API_KEY': api_key,
            'API_SECRET': api_secret,
        }

        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
        MEDIA_URL = f'https://res.cloudinary.com/{cloud_name}/image/upload/'

        print(f"✅ Cloudinary successfully configured for cloud: {cloud_name}")

    except Exception as e:
        print(f"❌ Error parsing CLOUDINARY_URL: {e}")
        # Fallback на локальне зберігання при помилці
        MEDIA_URL = '/media/'
        MEDIA_ROOT = BASE_DIR / 'media'
else:
    # Якщо URL немає, спробуємо знайти окремі змінні (на всяк випадок)
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    if cloud_name:
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': cloud_name,
            'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
            'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
        }
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
        MEDIA_URL = f'https://res.cloudinary.com/{cloud_name}/image/upload/'
    else:
        # Локальний режим
        print("⚠️ No Cloudinary config found. Using local storage.")
        MEDIA_URL = '/media/'
        MEDIA_ROOT = BASE_DIR / 'media'

# ======== General ========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# ======== Email ========
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "Nazarshylo2005@gmail.com"
EMAIL_HOST_PASSWORD = "yyhd onkt maud cvdz"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ======== Celery defaults ========
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'