import os
from django.core.asgi import get_asgi_application

# 1. Встановлюємо налаштування (навіть якщо Supervisor їх вже задав)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings.production')

# 2. 🔥 КРИТИЧНО: Ініціалізуємо додаток. ЦЕ МАЄ БУТИ ПЕРШИМ, ЩО ЗАПУСКАЄ DJANGO.
# Всі необхідні імпорти мають бути ПІСЛЯ цього рядка.
django_asgi_app = get_asgi_application()

# 3. Тільки ТЕПЕР імпортуємо решту, оскільки Django готовий.
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