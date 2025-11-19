from django.db import models, IntegrityError, transaction
from django.contrib.auth.models import User
from unidecode import unidecode
from django.utils.text import slugify
from django.urls import reverse
from decimal import Decimal
from django.core.validators import MinValueValidator
import uuid
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.utils import cloudinary_url
from django.conf import settings

import uuid
from django.db import IntegrityError, transaction
from django.utils.text import slugify
from unidecode import unidecode

class AD(models.Model):
    title = models.CharField(max_length=75)
    body = models.TextField(max_length=150)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    place = models.CharField(max_length=50)
    image = CloudinaryField('image', blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_ads', blank=True)
    views = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title

    def _generate_base_slug(self):
        # Генеруємо базовий slug із title або fallback 'ad'
        base = slugify(unidecode(self.title)) if self.title else ''
        return base or 'ad'

    def save(self, *args, **kwargs):
        # Якщо slug вже є — не змінюємо (щоб не ламати посилання)
        if not self.slug:
            base = self._generate_base_slug()

            # Обмежуємо довжину бази так, щоб суфікс вмістився в поле
            max_len = self._meta.get_field('slug').max_length
            # Залишимо місце для суфікса "-n" або "-<uuid6>"
            reserve = 8
            base = base[: max_len - reserve]

            candidate = base
            counter = 1
            tried_uuid = False

            # Пробуємо кілька разів уникнути колізій у Python-процесі
            while AD.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{counter}"
                counter += 1
                # Якщо занадто багато спроб — використаємо короткий uuid
                if counter > 50:
                    candidate = f"{base}-{uuid.uuid4().hex[:6]}"
                    tried_uuid = True
                    break

            self.slug = candidate

            # Збереження з захистом від race condition: якщо під час save іншій процес створив такий slug,
            # ловимо IntegrityError і пробуємо ще раз кілька разів.
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    # Якщо вже були uuid fallback — генеруємо ще один короткий uuid
                    if tried_uuid:
                        self.slug = f"{base}-{uuid.uuid4().hex[:6]}"
                    else:
                        # Якщо не було uuid, додаємо лічильник
                        self.slug = f"{base}-{counter}"
                        counter += 1
                    tried_uuid = True
                    # і пробуємо знову
                    continue

        else:
            # Якщо slug вже є — проста операція збереження
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ad_detail', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('ad_edit', kwargs={'slug': self.slug})


class AdImage(models.Model):
    # Посилання на оголошення (AD). related_name='images' дозволяє викликати ad.images.all()
    ad = models.ForeignKey('AD', on_delete=models.CASCADE, related_name='images')

    # Саме поле зображення
    image = CloudinaryField('image', blank=True, null=True)

    class Meta:
        verbose_name = "Додаткове зображення"
        verbose_name_plural = "Додаткові зображення"

    def __str__(self):
        return f"Image for {self.ad.title}"

DEFAULT_CLOUDINARY_IMAGE_ID = "xoe34jkbrrv8lr7mfpk8"  # твій default public_id


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)

    @property
    def image_url(self):
        """Повертає основне фото або дефолтне"""
        if self.image and getattr(self.image, "url", None):
            return self.image.url.replace("http://", "https://")

        # Якщо немає головного фото, беремо перше з AdImage
        first_image = self.images.first()
        if first_image and getattr(first_image.image, "url", None):
            return first_image.image.url.replace("http://", "https://")

        # Якщо і там немає — повертаємо дефолт Cloudinary або static
        url, _ = cloudinary_url(DEFAULT_CLOUDINARY_IMAGE_ID, secure=True)
        return url


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Автоматично створює або оновлює профіль користувача."""
    if created:
        # створюємо профіль із дефолтним фото
        Profile.objects.create(
            user=instance,
            image=DEFAULT_CLOUDINARY_IMAGE_ID
        )
    else:
        # якщо профіль існує — зберігаємо зміни
        instance.profile.save()

class ChatRoom(models.Model):
    """
    Модель для кімнати чату, прив'язаної до оголошення.
    (ЄДИНА ВЕРСІЯ)
    """
    ad = models.ForeignKey(
        AD,
        on_delete=models.CASCADE,
        related_name="chat_rooms"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chat_rooms"
    )

    def __str__(self):
        return f"Чат для оголошення: {self.ad.title}"

    def get_last_message(self):
        """Повертає останнє повідомлення в цьому чаті."""
        return self.messages.order_by('-timestamp').first()

    def get_other_participant(self, user):
        """Повертає іншого учасника чату, окрім поточного користувача."""
        participants = self.participants.all()
        # Перевіряємо, чи користувач взагалі є учасником
        if user in participants:
            return participants.exclude(id=user.id).first()
        # Якщо з якоїсь причини ні - повертаємо першого, кого знайдемо
        return participants.first()


class ChatMessage(models.Model):
    """
    Модель для окремого повідомлення в чаті.
    """
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # --- ДОДАЙТЕ ЦЕЙ РЯДОК ---
    is_read = models.BooleanField(default=False)
    file = CloudinaryField('chat_file', null=True, blank=True)
    # -------------------------

    def __str__(self):
        return f"Повідомлення від {self.sender.username} в {self.room.ad.title}"

    class Meta:
        ordering = ['timestamp']



class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='sent_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Тип сповіщення (на майбутнє, якщо будуть лайки або системні повідомлення)
    TYPE_CHOICES = (
        ('message', 'Повідомлення'),
        ('system', 'Системне'),
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='message')

    class Meta:
        ordering = ['-created_at']  # Спочатку нові

    def __str__(self):
        return f"Сповіщення для {self.recipient}: {self.message[:20]}..."