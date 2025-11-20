import os
from .base import *
import re
import dj_database_url

print("🚀 Running in PRODUCTION mode")

DEBUG = False

# 1. Отримуємо хости з ENV або використовуємо дефолтний
allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "sobes-prod-production.up.railway.app")
ALLOWED_HOSTS = allowed_hosts_env.split(",")

# ======== Database ========
print("✅ Connecting to PRODUCTION PostgreSQL database...")
database_url = os.environ.get('DATABASE_URL')

DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        ssl_require=False
    )
}

# 🚨 БЕЗПЕКА: Ніколи не виводьте DATABASE_URL повністю, бо там пароль!
if database_url:
    print("✅ DATABASE_URL found (Password hidden)")
else:
    print("❌ DATABASE_URL is missing!")

# ======== Redis Cache ========
redis_url = os.getenv("REDIS_URL")
if redis_url:
    print("✅ Connecting to PRODUCTION Redis...")
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": redis_url, # Зазвичай Railway дає повний URL, /1 не завжди потрібен
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
    # Якщо є Redis, використовуємо його для результатів Celery
    CELERY_RESULT_BACKEND = redis_url
else:
    CELERY_RESULT_BACKEND = "django-db"

# ======== Security (HTTPS & CSRF) ========

# 2. Це налаштування каже Django: "Якщо запит прийшов через Railway (Nginx/Proxy), вважай його HTTPS"
# Без цього ви отримаєте нескінченний редірект або помилку.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Примусовий редірект всіх на HTTPS
SECURE_SSL_REDIRECT = False

# Інші налаштування безпеки
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# 🚨 HSTS (ОБОВ'ЯЗКОВО ВИМКНУТИ ДЛЯ HTTP)
SECURE_HSTS_SECONDS = 0            # Було 31536000 -> стало 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# 3. CSRF Trusted Origins
# Автоматично додаємо https:// до всіх доменів з ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = [
    "http://193.56.151.227",
    "http://193.56.151.227:8000"
]
# Якщо потрібно додати ще щось вручну, розкоментуйте і додайте сюди:
# CSRF_TRUSTED_ORIGINS.extend([
#     "https://my-custom-domain.com",
#     "https://sobes-app-production-d2a1.up.railway.app"
# ])

print(f"✅ Allowed Hosts: {ALLOWED_HOSTS}")
print(f"✅ CSRF Trusted Origins: {CSRF_TRUSTED_ORIGINS}")