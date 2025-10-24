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

POSTGRES_HOST = get_env_variable('POSTGRES_HOST', 'db') # 'db' - це ім'я сервісу у docker-compose
POSTGRES_PORT = get_env_variable('POSTGRES_PORT', '5432')

DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
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

REDIS_HOST = get_env_variable('REDIS_HOST', 'redis') # 'redis' - це ім'я сервісу
REDIS_PORT = get_env_variable('REDIS_PORT', '6379')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1", # Використовуємо змінну хоста
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# ==============================================================================
# 4. НАЛАШТУВАННЯ CELERY
# ==============================================================================

RABBITMQ_HOST = get_env_variable('RABBITMQ_HOST', 'rabbitmq') # 'rabbitmq' - це ім'я сервісу
RABBITMQ_USER = get_env_variable('RABBITMQ_DEFAULT_USER', 'user')
RABBITMQ_PASS = get_env_variable('RABBITMQ_DEFAULT_PASS', 'password')
RABBITMQ_PORT = get_env_variable('RABBITMQ_PORT', '5672')

# Брокер (RabbitMQ)
CELERY_BROKER_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//'

# Backend (Redis) - для зберігання результатів завдань
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'

# Стандарти Celery
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
