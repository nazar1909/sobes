import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import myapp.routing # <--- Посилання на майбутній файл

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(), # Звичайні HTTP-запити
    
    # WebSocket-запити
    "websocket": AuthMiddlewareStack(
        URLRouter(
            myapp.routing.websocket_urlpatterns
        )
    ),
})