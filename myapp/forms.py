from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django import forms
from django.db.models.query import ValuesIterable
from .models import AD,Profile,AdImage
from . import models
from django.forms import inlineformset_factory
from PIL import Image
from django.forms.models import BaseInlineFormSet
from cloudinary.forms import CloudinaryFileField # 👈 ВАЖЛИВИЙ ІМПОРТ

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'password1': forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
            'password2': forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        }


MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_PREFIX = 'image/'

class AdForm(forms.ModelForm):
    class Meta:
        model = AD
        fields = ['title', 'price', 'body', 'place']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_attrs = {
            'title': {'placeholder': 'Наприклад, iPhone 11 з гарантією'},
            'price': {'placeholder': '0'},
            'body': {'placeholder': 'Подумайте, що хотів би дізнатися покупець...', 'rows': 5},
            'place': {'placeholder': 'Наприклад, Львів'},
        }
        for field_name, attrs in field_attrs.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': 'form-control', **attrs})





class AdImageForm(forms.ModelForm):
    # Явно перевизначаємо поле, щоб CloudinaryFileField гарантував правильний Public ID.
    image = CloudinaryFileField(
        options={
            'folder': 'ad_images_uploads',
            'tags': ['ad_image']
        },
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*', 'class': 'd-none'})
    )

    class Meta:
        model = AdImage
        fields = ['image']


# Кастомний BaseInlineFormSet для валідації мінімальної кількості фото
class BaseAdImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        # 🟢 FIX 1: Забезпечуємо, що загальна валідація пройшла (уникаємо помилок,
        # що виникають при спробі зберегти невалідований FormSet).
        if any(self.errors):
            return

        total = 0
        for form in self.forms:
            # 🟢 FIX 2: Використовуємо self.can_delete для більш точної перевірки
            # Якщо дані форми валідні (cleaned_data існує)
            if form.cleaned_data:
                data = form.cleaned_data

                # Перевіряємо, чи форма не позначена на видалення і містить файл
                if not data.get(forms.formsets.DELETION_FIELD_NAME, False) and data.get('image'):
                    total += 1

        if total < 1:
            raise ValidationError("Мінімум одне фото обов'язкове.")


# --- ВАЖЛИВО: це оголошення на рівні модуля (НЕ всередині класу) ---
AdImageFormSet = inlineformset_factory(
    AD,
    AdImage,
    form=AdImageForm,
    formset=BaseAdImageInlineFormSet,
    fields=['image'],
    extra=7,
    max_num=7,
    can_delete=True,
    # 🟢 FIX 3: Видаляємо надлишкову валідацію, щоб уникнути конфліктів.
    # validate_max=True залишаємо для обмеження max_num
    validate_max=True,
    # validate_min=True та min_num=1 видалено, оскільки це робить BaseAdImageInlineFormSet.
)
class OrderForm(forms.Form):
    name = forms.CharField(label="Ім’я", max_length=100)
    email = forms.EmailField(label="Електронна пошта")
    phone = forms.CharField(label="Номер телефону", max_length=20)


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Електронна пошта")



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'bio', 'image', 'phone', 'location']
        labels = {
            'full_name': 'Імʼя користувача',
            'bio': 'Опис',
            'image': 'Фото профілю',
            'phone': 'Телефон',
            'location': 'Місцезнаходження',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть імʼя користувача'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Розкажіть про себе',
                'rows': 3
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+380XXXXXXXXX'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше місто або країна'
            }),
        }