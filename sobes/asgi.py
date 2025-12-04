import os
import django
from django.core.asgi import get_asgi_application

# 1. Налаштування
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings.production')

# 2. Ініціалізація
django.setup()

# 3. Імпорти (ТІЛЬКИ НЕОБХІДНІ)
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from myapp.routing import websocket_urlpatterns

# 4. Стек: HTTP -> Django, WebSocket -> Auth -> URLRouter
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})