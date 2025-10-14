from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django import forms
from django.db.models.query import ValuesIterable

from . import models



class CustomUserCreationForm(UserCreationForm):
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username.isdigit:
            raise ValidationError("error")
        return username

    class Meta:
        model = User
        fields = ( "username", "email", "password1", "password2")

class AdForm(forms.ModelForm):
    class Meta:
        model = models.AD
        fields=("title","body","image","price")

class OrderForm(forms.Form):
    name = forms.CharField(label="Ім’я", max_length=100)
    email = forms.EmailField(label="Електронна пошта")
    phone = forms.CharField(label="Номер телефону", max_length=20)


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Електронна пошта")
