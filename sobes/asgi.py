import os
from django.core.asgi import get_asgi_application

# 1. Встановлюємо налаштування (ОБОВ'ЯЗКОВО ПЕРЕД get_asgi_application)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings.production')

# 2. 🔥 КРИТИЧНО: Ініціалізуємо додаток. ЦЕ ЗАВЖДИ ПЕРШЕ.
# Ми більше не робимо явний import myapp.routing на верхньому рівні!
django_asgi_app = get_asgi_application()

# 3. Тільки ТЕПЕР робимо імпорти, які залежать від Django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
# from myapp.routing import websocket_urlpatterns  <-- ПРИБИРАЄМО ЗВІДСИ!

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                # 🔥 ВАЖЛИВО: Імпортуємо routing.py ТУТ, ЛІНИВО (lazy import)
                # Це змушує Python імпортувати файл, тільки коли він потрібен.
                # Він уже пройшов усі перевірки безпеки.
                [
                    *__import__('myapp.routing', fromlist=['websocket_urlpatterns']).websocket_urlpatterns
                ]
            )
        )
    ),
})