"""
Django settings for sobes project.
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import sys
from distutils.util import strtobool

# Base dir (як ти мав)
BASE_DIR = Path(__file__).resolve().parent.parent

# Static
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media (буде визначено далі залежно від DEBUG)
DEFAULT_MEDIA_DIR = BASE_DIR / "media"

# Helper для env
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

# Secret & Debug
SECRET_KEY = get_env_variable('SECRET_KEY', 'django-insecure-PLACEHOLDER')
DEBUG = bool_env('DEBUG', default=True)

# Hosts / CORS
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS")

if ALLOWED_HOSTS:
    ALLOWED_HOSTS = ALLOWED_HOSTS.split(",")
else:
    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "sobes-app-production-d2a1.up.railway.app",
    ]# Для розвитку можна залишити '*', але у production краще передати список доменів у env.
CSRF_TRUSTED_ORIGINS = [
    "https://sobes-app-production-d2a1.up.railway.app",
]

CORS_ALLOW_ALL_ORIGINS = bool_env('CORS_ALLOW_ALL_ORIGINS', default=False)

# Installed apps (твій список + cloudinary)
INSTALLED_APPS = [
    'myapp.apps.MyappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'widget_tweaks',
    'wait_for_db_app',
    'django_celery_results',
    # cloudinary додамо умовно далі лише якщо налаштовано
]

# Cloudinary: увімкнути у production, якщо є CLOUDINARY_URL
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')  # може бути None

if CLOUDINARY_URL:
    # переконайтеся, що пакети встановлені: pip install cloudinary django-cloudinary-storage
    INSTALLED_APPS += ['cloudinary', 'cloudinary_storage']
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')  # опціонально
    MEDIA_URL = f'https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME or CLOUDINARY_URL.split("@")[-1]}/image/upload/'
    MEDIA_ROOT = DEFAULT_MEDIA_DIR  # не використовується для зберігання, але корисний fallback
else:
    # fallback: локальне зберігання (для DEBUG / локальної розробки)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = DEFAULT_MEDIA_DIR

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security suggestions for production
if not DEBUG:
    # Поради — включай у prod
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 рік; налаштуй поступово
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = bool_env('SECURE_SSL_REDIRECT', default=True)

# Django default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'





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
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

ROOT_URLCONF = 'sobes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sobes.wsgi.application'

# ==============================================================================
# 2. НАЛАШТУВАННЯ БАЗИ ДАНИХ (POSTGRES / SQLITE)
# ==============================================================================

# Спробуємо отримати DATABASE_URL із середовища (Railway, Render, Docker)
db_url_from_env = os.environ.get('DATABASE_URL')

if db_url_from_env:
    # --- ПРОДАКШН / RAILWAY / DOCKER ---
    print("✅ Connecting to PRODUCTION PostgreSQL database...")

    # Якщо DATABASE_URL передано як bytes — декодуємо
    if isinstance(db_url_from_env, bytes):
        db_url_from_env = db_url_from_env.decode('utf-8')

    # Парсимо DATABASE_URL (Railway автоматично створює її)
    DATABASES = {
        'default': dj_database_url.parse(db_url_from_env, conn_max_age=600)
    }

else:
    # --- ЛОКАЛЬНА РОЗРОБКА ---
    print("💻 Connecting to LOCAL SQLite database...")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# EMAIL SETTINGS (залишаємо ваші)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "Nazarshylo2005@gmail.com"
EMAIL_HOST_PASSWORD = "yyhd onkt maud cvdz"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==============================================================================
# 3. НАЛАШТУВАННЯ REDIS (Кешування)
# ==============================================================================

# Шукаємо змінну REDIS_URL, яку надає Railway
redis_url_from_env = os.environ.get('REDIS_URL')

if redis_url_from_env:
    # --- ЯКЩО МИ НА RAILWAY (PRODUCTION) ---
    print("Connecting to PRODUCTION Redis...")
    if isinstance(redis_url_from_env, bytes):
        redis_url_from_env = redis_url_from_env.decode('utf-8')

    CACHE_LOCATION = f"{redis_url_from_env}/1"

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": CACHE_LOCATION,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"}
        }
    }
else:
    # --- ЯКЩО МИ ЛОКАЛЬНО (DEVELOPMENT) ---
    print("Using LOCAL cache (in-memory)...")

    # Використовуємо просту "in-memory" заглушку замість Redis
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
# ==============================================================================
# 4. НАЛАШТУВАННЯ CELERY
# ==============================================================================

# 🛑 АБСОЛЮТНА ПРИМУСОВА ПЕРЕВІРКА ДЛЯ ЛОКАЛЬНОГО SHELL/RUNSERVER
# Визначаємо, чи ми виконуємо команду, яка вимагає синхронного режиму (shell, runserver, test)
# Виключаємо Production, перевіряючи відсутність DATABASE_URL (найбільш надійний індикатор Railway)
IS_LOCALLY_RUNNING = not os.environ.get('DATABASE_URL') and any(
    arg in sys.argv for arg in ['shell', 'runserver', 'test', 'celery'])

if IS_LOCALLY_RUNNING:
    # --- ЯКЩО МИ ЛОКАЛЬНО (ПРИМУСОВИЙ EAGER РЕЖИМ) ---
    print(">>> (FORCED LOCAL) Celery running in EAGER mode. RabbitMQ connection skipped.")

    # Це примусово ігнорує будь-які RABBITMQ_HOST змінні
    CELERY_BROKER_URL = 'memory://'
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_RESULT_BACKEND = 'django-db'

# --- Логіка Production залишається чистою ---

elif os.environ.get('RABBITMQ_HOST'):
    # --- ЯКЩО МИ НА RAILWAY (PRODUCTION) ---
    print("Connecting to PRODUCTION Celery (RabbitMQ)...")

    RABBITMQ_HOST = get_env_variable('RABBITMQ_HOST')
    RABBITMQ_USER = get_env_variable('RABBITMQ_DEFAULT_USER')
    RABBITMQ_PASS = get_env_variable('RABBITMQ_DEFAULT_PASS')
    RABBITMQ_PORT = get_env_variable('RABBITMQ_PORT')

    CELERY_BROKER_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//'

    if 'redis_url_from_env' in locals() and redis_url_from_env:
        CELERY_RESULT_BACKEND = f"{redis_url_from_env}/2"
    else:
        CELERY_RESULT_BACKEND = None

# --- Стандарти Celery ---
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'