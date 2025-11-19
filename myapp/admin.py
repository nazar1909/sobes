from django.contrib import admin
from .models import AD, ChatRoom, ChatMessage, Profile,Notification


@admin.register(AD)
class ADAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'views')  # Додав views, корисно бачити
    list_filter = ('user', 'date')
    search_fields = ('title', 'body')

    # Логіка: звичайний юзер бачить тільки свої оголошення, адмін - всі
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'ad', 'get_participants_count']

    def get_participants_count(self, obj):
        return obj.participants.count()

    get_participants_count.short_description = 'Participants'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    # Показуємо: хто написав, в якій кімнаті, коли і шматок тексту
    list_display = ['sender', 'room', 'timestamp', 'short_content']
    list_filter = ['timestamp', 'room']
    search_fields = ['content', 'sender__username']

    # Щоб не виводити все повідомлення в список, якщо воно довге
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    short_content.short_description = 'Message'


# Реєструємо профіль (простий варіант)
admin.site.register(Profile)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'short_message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['message', 'recipient__username', 'sender__username']

    def short_message(self, obj):
        return obj.message[:50]