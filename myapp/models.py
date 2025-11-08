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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 🔸 Генерація slug, якщо ще не створений
        if not self.slug:
            base_slug = slugify(unidecode(self.title)) or "ad"
            slug_candidate = base_slug
            counter = 1
            while AD.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{uuid.uuid4().hex[:6]}"
                counter += 1
                if counter > 10:
                    break
            self.slug = slug_candidate

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