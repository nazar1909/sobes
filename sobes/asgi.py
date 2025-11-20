import os
from django.core.asgi import get_asgi_application

# 1. Спочатку вказуємо налаштування
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings')

# 2. ВАЖЛИВО: Ініціалізуємо Django тут.
# Це завантажить усі додатки та моделі.
django_asgi_app = get_asgi_application()

# 3. Тільки ТЕПЕР імпортуємо роутинг і канали
# (бо тепер Django готовий і моделі можна використовувати)
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import myapp.routing

application = ProtocolTypeRouter({
    # Тут використовуємо вже створену змінну
    "http": django_asgi_app,

    "websocket": AuthMiddlewareStack(
        URLRouter(
            myapp.routing.websocket_urlpatterns
        )
    ),
})