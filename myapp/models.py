from django.db import models,IntegrityError, transaction
from django.contrib.auth.models import User
from unidecode import unidecode
from django.utils.text import slugify
from django.urls import reverse
from decimal import Decimal
from django.core.validators import MinValueValidator
import uuid


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
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_ads', blank=True)
    main_image = models.ImageField(
        upload_to='ad_images/',
        default='static/media/images/placeholder.png',  # 🧠 ось це ключове
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            # Використовуємо unidecode щоб перетворити кирилицю в латиницю
            base_slug = slugify(unidecode(self.title)) or "ad"
            slug_candidate = base_slug
            counter = 1
            while AD.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{uuid.uuid4().hex[:6]}"
                counter += 1
                if counter > 10:  # обмеження 10 спроб
                    break
            self.slug = slug_candidate

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ad_detail', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('ad_edit', kwargs={'slug': self.slug})


class AdImage(models.Model):
    ad = models.ForeignKey(AD, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ad_images/',null=True, blank=True)

    def __str__(self):
        return f"Image for {self.ad.title}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def get_full_name(self):
        return self.full_name or self.user.get_full_name() or self.user.username