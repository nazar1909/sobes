import os
from django.core.asgi import get_asgi_application

# 1. Встановлюємо налаштування
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings.production')

# 2. 🔥 КРИТИЧНО ВАЖЛИВО: Ініціалізуємо Django ТУТ
# Це завантажує INSTALLED_APPS і готує моделі.
# Якщо зробити імпорт нижче до цього рядка — буде помилка.
django_asgi_app = get_asgi_application()

# 3. Тільки ТЕПЕР імпортуємо Channels і твої маршрути
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from myapp.routing import websocket_urlpatterns

# 4. Збираємо все разом
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})