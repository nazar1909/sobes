from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django import forms
from django.db.models.query import ValuesIterable
from .models import AD,Profile
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
        # Переконайтеся, що 'image' тут!
        fields = ['title', 'price', 'body', 'place', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🟢 ОНОВЛЕНА ЛОГІКА СТИЛІЗАЦІЇ
        field_attrs = {
            'title': {'placeholder': 'Наприклад, iPhone 11 з гарантією'},
            'price': {'placeholder': '0'},
            # Зверніть увагу: 'body' потребує 'rows'
            'body': {'placeholder': 'Подумайте, що хотів би дізнатися покупець...', 'rows': 5},
            'place': {'placeholder': 'Наприклад, Львів'},
            'image': {'accept': 'image/*'}
        }

        for field_name, attrs in field_attrs.items():
            if field_name in self.fields:
                # ❗️ Забезпечуємо наявність form-control
                current_attrs = self.fields[field_name].widget.attrs
                current_attrs.update({'class': 'form-control', **attrs})

                # Додавання is-invalid при помилках
                if self.errors.get(field_name):
                    current_classes = current_attrs.get('class', '')
                    current_attrs['class'] = f'{current_classes} is-invalid'.strip()



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