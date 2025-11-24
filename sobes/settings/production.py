import os
import dj_database_url
from .base import * # Імпортуємо всі налаштування з base.py

print("🚀 Running in PRODUCTION mode (Fixed Configuration)")

DEBUG = False

# ==========================================
# 1. ALLOWED HOSTS
# ==========================================
allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = allowed_hosts_env.split(",")
# Додаємо ваш IP та домен вручну
if "193.56.151.227" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("193.56.151.227")
if "sobes-prod-production.up.railway.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("sobes-prod-production.up.railway.app")


# ==========================================
# 2. DATABASE (PostgreSQL)
# ==========================================
database_url = os.environ.get('DATABASE_URL')
if database_url:
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
    # Channels Configuration
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [redis_url],
            },
        },
    }
else:
    # Fallback if no redis provided (але для каналів потрібен Redis)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
    # Для Channels краще використати Redis, але якщо його немає:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
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
# Увімкніть це, якщо у вас є HTTPS (через Cloudflare або Nginx)
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    "http://193.56.151.227",
    "http://193.56.151.227:8000",
    "https://sobes-prod-production.up.railway.app",
]

# Статика вже налаштована в base.py, але підтверджуємо рут
print(f"✅ Config loaded. Static Root: {STATIC_ROOT}")