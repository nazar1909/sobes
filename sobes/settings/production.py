from .base import *
import re

print("🚀 Running in PRODUCTION mode")

DEBUG = False
ALLOWED_HOSTS = ["yourdomain.com", "www.yourdomain.com"]

# ======== Database ========
print("✅ Connecting to PRODUCTION PostgreSQL database...")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "sobes-db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# ======== Redis Cache ========
redis_url = os.getenv("REDIS_URL")
if redis_url:
    print("✅ Connecting to PRODUCTION Redis...")
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"{redis_url}/1",
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    print("⚠️ No REDIS_URL found — using local memory cache")
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# ======== Celery ========
print("⚙️ Connecting to Celery (RabbitMQ + Redis)")
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")

CELERY_BROKER_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"
CELERY_TASK_ALWAYS_EAGER = False

if redis_url:
    CELERY_RESULT_BACKEND = re.sub(r"/\d+$", "/2", redis_url)
else:
    CELERY_RESULT_BACKEND = "django-db"

# ======== Security ========
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
