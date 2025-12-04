# myapp/routing.py
from django.urls import re_path
from .consumers import ChatConsumer, NotificationConsumer

websocket_urlpatterns = [
    # 1. Маршрут для ЧАТУ (для конкретної кімнати)
    # Ми використовуємо (?P<room_name>[^/]+) замість \w+, щоб дозволити більше символів у slug
    re_path(r'ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer.as_asgi()),

    # 2. 🔥 МАРШРУТ ДЛЯ СПОВІЩЕНЬ (Персональний канал користувача) 🔥
    # Ми використовуємо (?P<user_id>\d+), щоб передати ID користувача в Consumer
    re_path(r'ws/notifications/(?P<user_id>\d+)/$', NotificationConsumer.as_asgi()),
]