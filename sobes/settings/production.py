import os
import dj_database_url
from .base import *

DEBUG = False

# ==========================================
# 1. ALLOWED HOSTS
# ==========================================
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "193.56.151.227", "sobes-prod-production.up.railway.app", "*"]

# ==========================================
# 2. DATABASE (PostgreSQL)
# ==========================================
# Беремо з Env, але якщо немає — ставимо локальні налаштування
database_url = os.environ.get('DATABASE_URL')

if database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            ssl_require=False
        )
    }
else:
    # Фолбек для локальної бази, якщо змінна злетіла
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'sobes',
            'USER': 'postgres',
            'PASSWORD': '12345678', # Твій пароль
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

# ==========================================
# 3. CACHE & REDIS (WebSockets)
# ==========================================
# 🔥 ЖОРСТКО ВКАЗУЄМО 127.0.0.1, ЩОБ ТОЧНО ПРАЦЮВАЛО
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Налаштування для ЧАТУ (Channels)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)], # Використовуємо локальні порти
        },
    },
}

# ==========================================
# 4. CELERY (RabbitMQ або Redis)
# ==========================================
# Якщо ти встановив RabbitMQ локально:
CELERY_BROKER_URL = "amqp://guest:guest@127.0.0.1:5672//"

# АБО, якщо RabbitMQ глючить, розкоментуй рядок нижче, щоб юзати Redis (це надійніше):
# CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_TASK_ALWAYS_EAGER = False

# ==========================================
# 5. SECURITY & HTTP
# ==========================================
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

CSRF_TRUSTED_ORIGINS = [
    "http://193.56.151.227",
    "http://193.56.151.227:8000",
    "http://193.56.151.227:8001",
    "https://sobes-prod-production.up.railway.app",
]

# Коментуємо, щоб не було помилки, якщо змінна не оголошена вище
# print(f"✅ Config loaded. Static Root: {STATIC_ROOT}")