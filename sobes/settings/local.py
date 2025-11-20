from .base import *
import os

print("✅ Running in LOCAL mode")

DEBUG = True
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]

# ======== Database ========
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "TEST"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "12345678"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# ======== Redis Cache (In-memory for local) ========
print("🧠 Using LOCAL cache (in-memory)")
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ======== Celery (Eager Mode) ========
# Eager mode означає, що задачі виконуються миттєво, без черги RabbitMQ/Redis
print(">>> Celery in EAGER mode")
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_ALWAYS_EAGER = True

# ======== Channels (WebSocket) ========
# Використовуємо Redis для WebSocket
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            # Якщо ви запускаєте локально (без Docker), тут має бути 127.0.0.1
            # Якщо через Docker Compose локально — то "redis"
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}