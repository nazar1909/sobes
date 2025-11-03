"""
Django settings for sobes project.
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# --- ДОДАЙТЕ ЦІ РЯДКИ ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Папка 'media' у корені проєкту
# -------------------------
CSRF_TRUSTED_ORIGINS = [
    'https://sobes-app-production-d2a1.up.railway.app',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ==============================================================================
# 1. ДОПОМІЖНА ФУНКЦІЯ ДЛЯ ЗЧИТУВАННЯ ЗМІННИХ СЕРЕДОВИЩА
# ==============================================================================

def get_env_variable(var_name, default_value=None):
    """
    Отримує змінну середовища.
    Якщо змінна не встановлена і немає значення за замовчуванням, викликає виняток.
    """
    value = os.environ.get(var_name)
    if value is not None:
        return value
    if default_value is not None:
        return default_value
    # Якщо змінна обов'язкова і не встановлена
    raise ImproperlyConfigured(f"Змінна середовища '{var_name}' не встановлена.")





# Quick-start development settings - unsuitable for production
# Зчитуємо SECRET_KEY та DEBUG із ENV, використовуючи значення за замовчуванням
SECRET_KEY = get_env_variable('SECRET_KEY', 'django-insecure-0k=^n2z+z7vkhx!g7&)%tpux!q27y$gg%p_ha9$yfec8nh3720')

# DEBUG має бути False у продакшені
DEBUG = get_env_variable('DEBUG', 'True') == 'True'

# Дозволяємо всі хости в Docker/Cloud
ALLOWED_HOSTS = ['*']

# Дозволяє підключення з будь-яких доменів
CORS_ALLOW_ALL_ORIGINS = True

# Або, для кращої безпеки, вкажи конкретні домени:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "https://my-frontend.vercel.app",
# ]

# Application definition

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
    'wait_for_db_app', # ДОДАНО: Для команди "wait_for_db"
]

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

# Шукаємо змінну DATABASE_URL, яку надає Railway
db_url_from_env = os.environ.get('DATABASE_URL')

if db_url_from_env:
    # --- ЯКЩО МИ НА RAILWAY (PRODUCTION) ---
    print("Connecting to PRODUCTION database (PostgreSQL)...")

    # Перевіряємо, чи це байти, і ДЕКОДУЄМО їх
    if isinstance(db_url_from_env, bytes):
        db_url_from_env = db_url_from_env.decode('utf-8')

    # Парсимо URL для Postgres
    DATABASES = {
        'default': dj_database_url.parse(db_url_from_env)
    }
else:
    # --- ЯКЩО МИ ЛОКАЛЬНО (DEVELOPMENT) ---
    print("Connecting to LOCAL database (sqlite3)...")

    # Використовуємо локальний файл db.sqlite3
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

# Перевіряємо, чи ми на Railway (використовуємо RABBITMQ_HOST як індикатор)
if os.environ.get('RABBITMQ_HOST'):
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
        CELERY_RESULT_BACKEND = None  # (Помилка, якщо Redis не підключений)

else:
    # --- ЯКЩО МИ ЛОКАЛЬНО (DEVELOPMENT) ---
    print("Using LOCAL Celery (running tasks synchronously)...")

    # Кажемо Celery виконувати всі завдання негайно,
    # не використовуючи RabbitMQ (який локально не запущений)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'django-db'

# --- Стандарти Celery ---
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

