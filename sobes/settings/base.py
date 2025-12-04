import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Завантаження змінних
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# ======== Helpers ========
def get_env_variable(name, default=None):
    return os.environ.get(name, default)

def bool_env(name, default=False):
    val = os.environ.get(name, str(default))
    return str(val).lower() in ("1", "true", "yes", "on")

# ======== Core ========
SECRET_KEY = 'django-insecure-FIXED-KEY-FOR-TESTING-123456789'
DEBUG = True # Локально True

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

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

    'cloudinary_storage',
    'django.contrib.staticfiles',

    'corsheaders',
    'widget_tweaks',
    'wait_for_db_app',
    'django_celery_results',
    'cloudinary',
    'rest_framework',
    'drf_spectacular',
]

# ======== Middleware ========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Локально WhiteNoise зручний
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

# ======== Static Files ========
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ======== Cloudinary ========
# Ті самі ключі
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dhact88gj',
    'API_KEY': '633531725433543',
    'API_SECRET': '1U31LQvhjYxWljoN8tBIx-i36hI'
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ======== Database ========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Локально можна SQLite
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ======== Others ========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# REST
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGE_SIZE': 12,
}