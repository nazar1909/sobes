import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage  # локальний імпорт
from .models import AD, ChatRoom  # локальний імпорт
from .models import ChatMessage
from .models import Profile  # локальний імпорт
from .models import Notification



class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_user_avatar_url(self, user):
        try:
            if hasattr(user, 'profile') and user.profile.image and user.profile.image.url:
                return user.profile.image.url
        except Exception:
            pass
        return '/static/images/default-avatar.png'

    @database_sync_to_async
    def get_chat_history(self, room):
        messages = ChatMessage.objects.filter(room=room).select_related('sender__profile').order_by('-timestamp')[:50]
        result = []
        for msg in reversed(messages):
            avatar = '/static/images/default-avatar.png'
            try:
                if hasattr(msg.sender, 'profile') and msg.sender.profile.image:
                    avatar = msg.sender.profile.image.url
            except:
                pass
            result.append({
                'username': msg.sender.username,
                'message': msg.content,
                'avatar_url': avatar,
                'timestamp': msg.timestamp.strftime("%H:%M")
            })
        return result

    @database_sync_to_async
    def get_or_create_room(self):
        ad = AD.objects.get(id=self.ad_id)
        buyer =  get_user_model().objects.get(id=self.buyer_id)

        chat = ChatRoom.objects.filter(ad=ad, participants=buyer).first()
        if not chat:
            chat = ChatRoom.objects.create(ad=ad)

        chat.participants.add(buyer, ad.user)
        return chat

    @database_sync_to_async
    def check_access(self, room, user):
        return room.participants.filter(id=user.id).exists()

    @database_sync_to_async
    def save_message(self, room, user, content):
        return ChatMessage.objects.create(room=room, sender=user, content=content)

    @database_sync_to_async
    def get_other_participants(self, room, sender):
        return list(room.participants.exclude(id=sender.id))

    @database_sync_to_async
    def create_notification(self, recipient, message):
        return Notification.objects.create(
            recipient=recipient,
            sender=self.user,
            message=message,
            notification_type='message'
        )

    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # 1. ІНІЦІАЛІЗАЦІЯ ОБОВ'ЯЗКОВИХ ЗМІННИХ ОДРАЗУ!
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'  # Тепер ця змінна точно існує!

        if '-' not in self.room_name:
            await self.close()
            return

        # 2. Перевірка та ініціалізація AD/BUYER
        try:
            ad, buyer = self.room_name.split('-')
            self.ad_id = int(ad)
            self.buyer_id = int(buyer)
        except ValueError:
            await self.close()
            return

        # 3. Приймаємо з'єднання (це має бути якомога раніше)
        await self.accept()  # <-- Підтверджуємо, що ми готові

        # 4. DB-логіка, яка може бути повільною:
        self.room = await self.get_or_create_room()
        allowed = await self.check_access(self.room, self.user)

        if not allowed:
            # Закриваємо з кодом 4003 (доступу немає)
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        history = await self.get_chat_history(self.room)
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': history
        }))

    async def disconnect(self, close_code):
        # 1. ОБРОБКА ВИКЛЮЧЕННЯ:
        # Ми перевіряємо, чи існує self.room_group_name, перш ніж намагатися його використати.
        try:
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
        except Exception as e:
            # Тут можна логувати помилку, але головне - не дати Daphne впасти.
            print(f"Помилка при відключенні: {e}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg = text_data_json['message']
        username = self.user.username
        avatar = await self.get_user_avatar_url(self.user)

        await self.save_message(self.room, self.user, msg)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg,
                'username': username,
                'avatar_url': avatar
            }
        )

        other = await self.get_other_participants(self.room, self.user)
        for r in other:
            notif = f"{username} написав вам"
            await self.create_notification(r, notif)

            await self.channel_layer.group_send(
                f"user_{r.id}_notifications",
                {
                    'type': 'chat_notification',
                    'message': notif,
                    'sender': username,
                    'content': msg,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'username': event['username'],
            'avatar_url': event['avatar_url']
        }))
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope['user'].id
        self.room_group_name = f'user_{user_id}_notifications'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_notification(self, event):
        # Пересилка сповіщення клієнту
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'message': event['message'],
            'sender': event['sender'],
            'content': event['content']
        }))