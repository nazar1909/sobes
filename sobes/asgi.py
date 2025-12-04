import os
import django # 🔥 ДОДАНО/ПЕРЕМІЩЕНО
from django.core.asgi import get_asgi_application

# 1. Встановлюємо налаштування (ОБОВ'ЯЗКОВО ПЕРШИМ)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings.production')

# 2. 🔥 ПРИМУСОВА ІНІЦІАЛІЗАЦІЯ 🔥
# Це гарантує, що INSTALLED_APPS завантажаться до імпорту моделей.
django.setup()

# 3. Тільки ТЕПЕР імпортуємо WebSockets і роутинг
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from myapp.routing import websocket_urlpatterns

# 4. Збираємо все разом
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})