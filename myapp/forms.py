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

    def clean_password1(self):
        """
        Валідація:
        1. Тільки англійські літери, цифри та спецсимволи (жодної кирилиці).
        2. Мінімум одна велика літера.
        3. Мінімум одна цифра.
        4. Мінімум один спецсимвол.
        """
        password = self.cleaned_data.get('password1')

        if password:
            # Список дозволених спецсимволів (можеш додати або прибрати зайві)
            special_chars_str = r'!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?'

            # 1. ПЕРЕВІРКА НА МОВУ (Тільки англійські літери + цифри + спецсимволи)
            # ^ - початок рядка, $ - кінець рядка.
            # [a-zA-Z0-9...] - дозволений набір.
            if not re.match(f'^[a-zA-Z0-9{re.escape(special_chars_str)}]+$', password):
                raise ValidationError(
                    "Пароль повинен містити тільки англійські літери, цифри та спецсимволи.",
                    code='password_invalid_chars'
                )

            # 2. Перевірка на велику літеру (A-Z)
            if not re.search(r'[A-Z]', password):
                raise ValidationError(
                    "Пароль повинен містити принаймні одну велику літеру (A-Z).",
                    code='password_no_upper'
                )

            # 3. Перевірка на цифру (0-9)
            if not re.search(r'\d', password):
                raise ValidationError(
                    "Пароль повинен містити принаймні одну цифру.",
                    code='password_no_digit'
                )

            # 4. Перевірка на спецсимвол
            if not re.search(f'[{re.escape(special_chars_str)}]', password):
                raise ValidationError(
                    "Пароль повинен містити принаймні один спецсимвол.",
                    code='password_no_special'
                )

        return password

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_PREFIX = 'image/'
ALLOWED_CITIES = [
    "Київ", "Львів", "Одеса", "Харків", "Дніпро",
    "Вінниця", "Полтава", "Івано-Франківськ", "Чернівці",
    "Ужгород", "Запоріжжя", "Миколаїв", "Хмельницький", "Рівне"
]

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
        if self.instance and getattr(self.instance, "place", None):
            if self.instance.place not in ALLOWED_CITIES:
                self.initial['place'] = ''

    def clean_place(self):
        place = self.cleaned_data.get('place').strip()
        if place not in ALLOWED_CITIES:
            raise ValidationError("❌ Вкажіть коректне місто зі списку." + ", ".join(ALLOWED_CITIES))
        return place



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
    min_num=1,
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
    comment = forms.CharField(
        label="Коментар до замовлення",
        max_length=300,
        required=False,  # Коментар зазвичай необов'язковий
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40})  # Встановлюємо початковий розмір
    )

    def clean_phone(self):
        phone_number = self.cleaned_data['phone']

        # 1. Перевірка, чи це рівно 9 символів
        if len(phone_number) != 9:
            raise forms.ValidationError("Номер телефону має містити рівно 9 цифр.")

        # 2. Перевірка, чи це лише цифри
        if not phone_number.isdigit():
            raise forms.ValidationError("Номер телефону може містити лише цифри (0-9).")

        # 3. Додаємо префікс +380 перед збереженням
        return f"+380{phone_number}"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['email'].initial = user.email
            self.fields['name'].initial = user.get_full_name() or user.username

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Електронна пошта")



class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label='Імʼя користувача',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть імʼя користувача'
        })
    )
    email = forms.EmailField(
        label='Пошта',
        required=False,
        disabled=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = Profile
        fields = ['image','phone']  # тільки поля профілю
        labels = {'phone': 'Телефон'}
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '971234567 (без 0 на початку)',  # Підказка важлива, бо вимагаємо 9 цифр
                'type': 'tel',
                'maxlength': '9'  # Обмежуємо ввід, щоб не вводили зайвого
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.user = user
            # якщо username є — вставляємо
            self.fields['username'].initial = user.username or ''
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if hasattr(self, 'user') and self.user:
            user = self.user
            username = self.cleaned_data.get('username', user.username)
            if username.strip():  # якщо користувач не стер повністю
                user.username = username
            if commit:
                user.save()
                profile.user = user
                profile.save()
        elif commit:
            profile.save()
        return profile