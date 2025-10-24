"""
Django settings for sobes project.
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import dj_database_url



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


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


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
    'myapp',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'wait_for_db_app', # ДОДАНО: Для команди "wait_for_db"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
# 2. НАЛАШТУВАННЯ БАЗИ ДАНИХ (POSTGRES)
# ==============================================================================

#Отримуємо змінну з Railway
db_url_from_env = os.environ.get('DATABASE_URL') # <--- ОСЬ ЦЕЙ РЯДОК ТИ ПРОПУСТИВ

# 1. Перевіряємо, чи вона взагалі є
if not db_url_from_env:
    raise ImproperlyConfigured("Змінна DATABASE_URL не встановлена або пуста.")

# 2. Перевіряємо, чи це байти, і ДЕКОДУЄМО їх
if isinstance(db_url_from_env, bytes):
    db_url_from_env = db_url_from_env.decode('utf-8')

# 3. Тепер парсимо чистий текст
DATABASES = {
    'default': dj_database_url.parse(db_url_from_env)
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

# Отримуємо змінну REDIS_URL з Railway
redis_url_from_env = os.environ.get('REDIS_URL')

if redis_url_from_env:
    # Перевіряємо, чи це байти (b''://), і ДЕКОДУЄМО їх
    if isinstance(redis_url_from_env, bytes):
        redis_url_from_env = redis_url_from_env.decode('utf-8')

    # Використовуємо /1 для кешу
    CACHE_LOCATION = f"{redis_url_from_env}/1"
else:
    # Запасний варіант для локального запуску, якщо REDIS_URL не встановлено
    CACHE_LOCATION = "redis://redis:6379/1"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# ==============================================================================
# 4. НАЛАШТУВАННЯ CELERY
# ==============================================================================

# --- БРОКЕР (RabbitMQ) ---
# Зчитуємо змінні, які ми вручну встановили для sobes-app
RABBITMQ_HOST = get_env_variable('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = get_env_variable('RABBITMQ_DEFAULT_USER', 'user')
RABBITMQ_PASS = get_env_variable('RABBITMQ_DEFAULT_PASS', 'password')
RABBITMQ_PORT = get_env_variable('RABBITMQ_PORT', '5672')

# Складаємо URL для брокера вручну
CELERY_BROKER_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//'


# --- BACKEND (Redis) ---
# Ми знову беремо REDIS_URL, але вказуємо іншу "базу даних" (наприклад, /2)
# щоб не плутати результати Celery з кешем.
# Ми беремо змінну redis_url_from_env з Секції 3 (див. нижче)

if 'redis_url_from_env' in locals() and redis_url_from_env:
    CELERY_RESULT_BACKEND = f"{redis_url_from_env}/2"
else:
    # Запасний варіант для локального запуску
    CELERY_RESULT_BACKEND = "redis://redis:6379/2"

# --- Стандарти Celery ---
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'