from .base import *

print("✅ Running in LOCAL mode")

DEBUG = True
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]

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

# Redis (optional)
print("🧠 Using LOCAL cache (in-memory)")
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Celery — виконує задачі синхронно (без брокера)
print(">>> Celery in EAGER mode")
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_ALWAYS_EAGER = True
# Налаштування для Django Channels (використовуємо ваш Redis)
from .base import *

print("✅ Running in LOCAL mode")

DEBUG = True
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]

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

# Redis (optional)
print("🧠 Using LOCAL cache (in-memory)")
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Celery — виконує задачі синхронно (без брокера)
print(">>> Celery in EAGER mode")
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_ALWAYS_EAGER = True
# Налаштування для Django Channels (використовуємо ваш Redis)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}