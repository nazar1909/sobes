# myapp/context_processors.py
from .models import Notification,ChatRoom


def notifications_count(request):
    if request.user.is_authenticated:
        # Рахуємо кількість КІМНАТ, в яких є хоча б одне непрочитане повідомлення,
        # відправлене НЕ поточним користувачем.
        count = ChatRoom.objects.filter(
            participants=request.user,  # Чати користувача
            messages__is_read=False  # Де є непрочитані повідомлення
        ).exclude(
            messages__sender=request.user  # І відправник не я сам
        ).distinct().count()  # distinct() щоб не рахувати одну кімнату двічі

        return {'unread_notifications_count': count}

    return {'unread_notifications_count': 0}