import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

# Імпорти моделей зверху - це правильно!
from .models import ChatMessage, AD, ChatRoom, Profile, Notification

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_user_avatar_url(self, user):
        try:
            if hasattr(user, 'profile') and user.profile.image and user.profile.image.url:
                return user.profile.image.url
        except Exception:
            pass
        return 'https://res.cloudinary.com/dhact88gj/image/upload/xoe34jkbrrv8lr7mfpk8'  # Краще використовувати абсолютний шлях або статичний URL

    @database_sync_to_async
    def get_chat_history(self, room):
        # Додано перевірку, чи кімната існує
        if not room:
            return []

        messages = ChatMessage.objects.filter(room=room).select_related('sender__profile').order_by('-timestamp')[:50]
        result = []
        for msg in reversed(messages):
            avatar = '/static/images/placeholder.png'
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
        try:
            # 🔥 ВИПРАВЛЕННЯ: Безпечне отримання об'єктів
            # Якщо ID не існує - повертаємо None, а не крашимо сервер
            try:
                ad = AD.objects.get(id=self.ad_id)
                buyer = User.objects.get(id=self.buyer_id)
            except ObjectDoesNotExist:
                return None  # Сигнал, що даних немає

            chat = ChatRoom.objects.filter(ad=ad, participants=buyer).first()
            if not chat:
                chat = ChatRoom.objects.create(ad=ad)

            # add() не дублює, якщо вже є
            chat.participants.add(buyer, ad.user)
            return chat
        except Exception as e:
            print(f"Error in get_or_create_room: {e}")
            return None

    @database_sync_to_async
    def check_access(self, room, user):
        if not room:
            return False
        return room.participants.filter(id=user.id).exists()

    @database_sync_to_async
    def save_message(self, room, user, content):
        if not room: return None
        return ChatMessage.objects.create(room=room, sender=user, content=content)

    @database_sync_to_async
    def get_other_participants(self, room, sender):
        if not room: return []
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
        from django.conf import settings
        print(f"DEBUG: SECRET_KEY start: {settings.SECRET_KEY[:5]}...")
        print(f"DEBUG: DB Name: {settings.DATABASES['default']['NAME']}")
        print(f"DEBUG: DB Host: {settings.DATABASES['default']['HOST']}")
        self.user = self.scope['user']
        print(f"DEBUG: User found: {self.user} (Is Auth: {self.user.is_authenticated})")
        # 1. Перевірка авторизації
        if not self.user.is_authenticated:
            await self.close()
            return

        # 2. Ініціалізація змінних (щоб disconnect не падав)
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
        except KeyError:
            await self.close()
            return

        if '-' not in self.room_name:
            await self.close()
            return

        try:
            ad_str, buyer_str = self.room_name.split('-')
            self.ad_id = int(ad_str)
            self.buyer_id = int(buyer_str)
        except ValueError:
            await self.close()
            return

        # 3. Приймаємо з'єднання (щоб клієнт не чекав DB)
        await self.accept()

        # 4. Отримуємо кімнату (безпечно)
        self.room = await self.get_or_create_room()

        # 🔥 ВИПРАВЛЕННЯ: Якщо кімнату не вдалося створити (напр. видалене оголошення)
        if self.room is None:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Chat not found or Ad deleted'
            }))
            await self.close(code=4004)  # Закриваємо коректно
            return

        # 5. Перевірка прав доступу
        allowed = await self.check_access(self.room, self.user)
        if not allowed:
            await self.close(code=4003)
            return

        # 6. Підписка на групу
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 7. Історія
        history = await self.get_chat_history(self.room)
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': history
        }))

    async def disconnect(self, close_code):
        # 🔥 ВИПРАВЛЕННЯ: Захист від падіння
        if hasattr(self, 'room_group_name'):
            try:
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            except Exception:
                pass

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            msg = text_data_json.get('message', '').strip()

            if not msg:
                return

            username = self.user.username
            avatar = await self.get_user_avatar_url(self.user)

            # Зберігаємо
            await self.save_message(self.room, self.user, msg)

            # Відправляємо в чат
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': msg,
                    'username': username,
                    'avatar_url': avatar
                }
            )

            # Сповіщення
            other = await self.get_other_participants(self.room, self.user)
            for r in other:
                notif_text = f"{username} написав вам"
                await self.create_notification(r, notif_text)

                await self.channel_layer.group_send(
                    f"user_{r.id}_notifications",
                    {
                        'type': 'chat_notification',
                        'message': notif_text,
                        'sender': username,
                        'content': msg,
                    }
                )
        except Exception as e:
            # Логуємо помилку, але не кладемо сервер
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'username': event['username'],
            'avatar_url': event['avatar_url']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"DEBUG: CONNECTING... Headers: {self.scope.get('headers')}")
        self.user = self.scope['user']
        print(f"DEBUG: User found: {self.user} (Is Auth: {self.user.is_authenticated})")

        # 🔥 ВИПРАВЛЕННЯ: Перевірка авторизації для сповіщень
        if not self.user.is_authenticated:
            print("DEBUG: REJECTING ANONYMOUS")
            await self.close()
            return

        self.room_group_name = f'user_{self.user.id}_notifications'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'message': event['message'],
            'sender': event['sender'],
            'content': event['content']
        }))