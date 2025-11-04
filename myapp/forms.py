from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django import forms
from django.db.models.query import ValuesIterable
from .models import AD,Profile,AdImage
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

class AdForm(forms.ModelForm):
    class Meta:
        model = AD
        # ❌ ВИДАЛЕНО: image (воно буде у FormSet)
        fields = ['title', 'price', 'body', 'place']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🟢 ОНОВЛЕНА ЛОГІКА СТИЛІЗАЦІЇ
        field_attrs = {
            'title': {'placeholder': 'Наприклад, iPhone 11 з гарантією'},
            'price': {'placeholder': '0'},
            'body': {'placeholder': 'Подумайте, що хотів би дізнатися покупець...', 'rows': 5},
            'place': {'placeholder': 'Наприклад, Львів'},
            # 'image' більше тут не стилізується
        }

        # ... (Ваша логіка застосування класів до інших полів) ...
        for field_name, attrs in field_attrs.items():
             if field_name in self.fields:
                current_attrs = self.fields[field_name].widget.attrs
                current_attrs.update({'class': 'form-control', **attrs})
# Форма для ОДНОГО зображення
class AdImageForm(forms.ModelForm):
    class Meta:
        model = AdImage
        fields = ['image']
    # ... (Ваша логіка __init__ для стилізації поля image) ...


# 🛑 ФУНКЦІЯ ВАЛІДАЦІЇ МІНІМУМУ
def clean_ad_image_formset(formset):
    count = 0
    for form in formset:
        if form.cleaned_data and not form.cleaned_data.get('DELETE'):
            count += 1
    if count < 1:
        raise ValidationError("Ви повинні завантажити щонайменше одне фото (мінімум 1).", code='min_images')
    return formset

# Formset для КІЛЬКОХ форм зображень (1 до 7)
AdImageFormSet = inlineformset_factory(
    AD,  # Батьківська модель
    AdImage,  # Дочірня модель
    form=AdImageForm,
    fields=['image'],
    extra=7,
    max_num=7,  # МАКСИМУМ
    min_num=1,  # МІНІМУМ (для автоматичної валідації formset)
    can_delete=True
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