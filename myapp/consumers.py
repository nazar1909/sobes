import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import AD, ChatRoom, ChatMessage, Notification

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    # --- Допоміжні методи роботи з БД ---

    @database_sync_to_async
    def get_user_avatar_url(self, user):
        try:
            if hasattr(user, 'profile') and user.profile.image and user.profile.image.url:
                return user.profile.image.url
        except Exception:
            pass
        # Замініть на шлях до вашої дефолтної картинки
        return '/static/images/default-avatar.png'

    @database_sync_to_async
    def get_chat_history(self, room):
        # Завантажуємо останні 50 повідомлень
        messages = room.messages.select_related('sender__profile').all().order_by('-timestamp')[:50]
        result = []
        for msg in reversed(messages):
            avatar_url = '/static/images/default-avatar.png'
            try:
                if hasattr(msg.sender, 'profile') and msg.sender.profile.image:
                    avatar_url = msg.sender.profile.image.url
            except Exception:
                pass
            result.append({
                'username': msg.sender.username,
                'message': msg.content,
                'avatar_url': avatar_url,
                'timestamp': msg.timestamp.strftime("%H:%M")
            })
        return result

    @database_sync_to_async
    def get_or_create_room(self):
        ad = AD.objects.get(id=self.ad_id)
        buyer = User.objects.get(id=self.buyer_id)

        # Шукаємо існуючий чат
        chat = ChatRoom.objects.filter(ad=ad).filter(participants=buyer).first()

        if not chat:
            chat = ChatRoom.objects.create(ad=ad)

        # Гарантуємо, що обидва користувачі є учасниками
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

    # --- WebSocket методи ---

    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Парсинг room_name (ad_id-buyer_id)
        if '-' in self.room_name:
            try:
                ad_id_str, buyer_id_str = self.room_name.split('-')
                self.ad_id = int(ad_id_str)
                self.buyer_id = int(buyer_id_str)

                self.room = await self.get_or_create_room()

                # Перевірка доступу
                is_allowed = await self.check_access(self.room, self.user)
                if not is_allowed:
                    print(f"⛔ Access denied for {self.user.username}")
                    await self.close()
                    return

            except ValueError:
                await self.close()
                return
        else:
            await self.close()
            return

        # Підключення до групи чату
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Відправка історії
        history = await self.get_chat_history(self.room)
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': history
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        username = self.user.username
        avatar_url = await self.get_user_avatar_url(self.user)

        # 1. Зберігаємо повідомлення в БД
        await self.save_message(self.room, self.user, message_content)

        # 2. Відправляємо повідомлення в групу ЧАТУ (щоб побачили обидва в чаті)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # Викликає метод chat_message нижче
                'message': message_content,
                'username': username,
                'avatar_url': avatar_url
            }
        )

        # 3. --- ЛОГІКА СПОВІЩЕНЬ ---
        other_participants = await self.get_other_participants(self.room, self.user)

        for recipient in other_participants:
            notif_text = f"{username} написав вам"

            # А. Зберігаємо сповіщення в БД
            await self.create_notification(recipient, notif_text)

            # Б. Відправляємо сигнал в особистий канал одержувача
            # Група називається: user_{id}_notifications
            recipient_group = f"user_{recipient.id}_notifications"

            print(f"🔔 Надсилаю сигнал у групу: {recipient_group}")

            await self.channel_layer.group_send(
                recipient_group,
                {
                    'type': 'chat_notification',  # 🔥 ВАЖЛИВО: Це шукає метод chat_notification у NotificationConsumer
                    'message': notif_text,
                    'sender': username,
                    'content': message_content,
                }
            )

    # Цей метод обробляє повідомлення всередині чату
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'username': event['username'],
            'avatar_url': event['avatar_url']
        }))


# --- СПОЖИВАЧ СПОВІЩЕНЬ (ОБОВ'ЯЗКОВИЙ) ---

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        # Унікальна група для кожного користувача
        self.group_name = f"user_{self.user.id}_notifications"

        print(f"✅ Notification Socket Connected: {self.group_name}")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # 🔥 Цей метод викликається, коли хтось робить group_send з type='chat_notification'
    async def chat_notification(self, event):
        print(f"📩 Notification received via WS: {event['message']}")

        # Відправляємо JSON на фронтенд (у JavaScript)
        await self.send(text_data=json.dumps({
            'type': 'chat_notification',
            'message': event['message'],
            'sender': event.get('sender'),
            'content': event.get('content')
        }))