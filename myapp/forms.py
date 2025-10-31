from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django import forms
from django.db.models.query import ValuesIterable
from .models import AD,AdImage,Profile
from . import models
from django.forms import inlineformset_factory



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

# Основна форма для оголошення (БЕЗ поля image)
class AdForm(forms.ModelForm):
    class Meta:
        model = AD
        fields = ['title', 'price', 'body', 'place']  # Тільки поля моделі AD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи та плейсхолдери Bootstrap
        self.fields['title'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Наприклад, iPhone 11 з гарантією'})
        self.fields['price'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': '0'})  # Додав плейсхолдер 0 для ціни
        self.fields['body'].widget.attrs.update(
            {'class': 'form-control', 'rows': 5, 'placeholder': 'Подумайте, що хотів би дізнатися покупець...'})
        self.fields['place'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Наприклад, Львів'})  # Додав плейсхолдер для місця

        # Додаємо клас is-invalid при помилках
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{current_classes} is-invalid'.strip()


# Форма для ОДНОГО зображення
class AdImageForm(forms.ModelForm):
    class Meta:
        model = AdImage
        fields = ['image']  # Тільки поле image з моделі AdImage

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо атрибути до поля image
        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*',  # Дозволяємо вибирати тільки зображення
        })
        # Додаємо is-invalid при помилці
        if self.errors.get('image'):
            current_classes = self.fields['image'].widget.attrs.get('class', '')
            self.fields['image'].widget.attrs['class'] = f'{current_classes} is-invalid'.strip()


# Formset для КІЛЬКОХ форм зображень (ВАЖЛИВО: має бути ПІСЛЯ AdImageForm)
AdImageFormSet = inlineformset_factory(
    AD,  # Батьківська модель
    AdImage,  # Дочірня модель
    form=AdImageForm,  # Використовуємо форму AdImageForm
    fields=['image'],  # Поле з AdImageForm
    extra=7,  # Показувати 1 порожню форму спочатку
    can_delete=True  # Дозволити видаляти фото при редагуванні
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