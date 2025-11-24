import os
import dj_database_url
from .base import * # Імпортуємо всі налаштування з base.py

print("🚀 Running in PRODUCTION mode (Fixed Configuration)")

DEBUG = False

# ==========================================
# 1. ALLOWED HOSTS
# ==========================================
allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "sobes-prod-production.up.railway.app,localhost,127.0.0.1")
ALLOWED_HOSTS = allowed_hosts_env.split(",")
# Додаємо ваш IP вручну
if "193.56.151.227" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("193.56.151.227")


# ==========================================
# 2. DATABASE (PostgreSQL)
# ==========================================
database_url = os.environ.get('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        ssl_require=False
    )
}


# ==========================================
# 3. CACHE & REDIS
# ==========================================
redis_url = os.getenv("REDIS_URL")
if redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": redis_url,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }


# ==========================================
# 4. CELERY
# ==========================================
CELERY_BROKER_URL = f"amqp://{os.getenv('RABBITMQ_DEFAULT_USER', 'guest')}:{os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')}@{os.getenv('RABBITMQ_HOST', 'rabbitmq')}:5672//"
CELERY_RESULT_BACKEND = redis_url if redis_url else "django-db"
CELERY_TASK_ALWAYS_EAGER = False


# ==========================================
# 5. SECURITY & HTTP
# ==========================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

CSRF_TRUSTED_ORIGINS = [
    "http://193.56.151.227",
    "http://193.56.151.227:8000",
    "ws://193.56.151.227:8000",
    "http://localhost:8000",
]


# ==========================================
# 🔥 ВИПРАВЛЕННЯ ДЛЯ CHANNELS (ЧАТ) 🔥
# ==========================================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}


# ==========================================
# 🔥 ВИПРАВЛЕННЯ ДЛЯ СТИЛІВ (WHITENOISE) 🔥
# ==========================================

# 1. Жорстко задаємо шлях до вихідних файлів у Docker
# (Це замінює BASE_DIR / "static", який працював неправильно)
STATICFILES_DIRS = [
    '/app/static',
]

# 2. Жорстко задаємо шлях, куди збирається статика
STATIC_ROOT = '/app/staticfiles'

# 3. Налаштування сховища (без хешування для стабільності)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# 4. Примусово вмикаємо WhiteNoise
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# 5. Перестраховка для медіа-файлів (теж абсолютні шляхи)
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

print(f"✅ Config loaded. Static Root: {STATIC_ROOT}")