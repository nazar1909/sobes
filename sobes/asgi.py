import os
import django
from django.core.asgi import get_asgi_application

# 1. Вказуємо налаштування
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings.production')

# 2. Ініціалізуємо Django (завантажуємо додатки)
django.setup()

# 3. Створюємо HTTP додаток (для звичайних сторінок)
django_asgi_app = get_asgi_application()

# 4. ТІЛЬКИ ТЕПЕР імпортуємо Channels і твій роутинг
# (бо моделі вже готові до використання)
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import myapp.routing  # <--- Цей імпорт має бути тут, внизу!

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            myapp.routing.websocket_urlpatterns
        )
    ),
})