from django.shortcuts import render,redirect,get_object_or_404
from .forms import CustomUserCreationForm
import re
from django.contrib.auth import login
from django.urls import reverse
from .forms import AdForm
from django.contrib.auth.decorators import login_required
from .models import AD
from django.core.mail import send_mail
from django.conf import settings
from .forms import OrderForm,PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.core.cache import cache

# Create your views here.
def home(request):
    ads = AD.objects.all()
    return render(request, 'main/index.html',{'ads': ads})


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print("Logged in:", request.user.username)
            return redirect("home")

    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def ad_create(request):
    if request.method == "POST":
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user   # Прив’язка до автора
            ad.save()
            return redirect("home")

    else:
        form = AdForm()
    return render(request, "myapp/ad_form.html", {"form": form})



def listing_detail(request,):
    ads = AD.objects.all()
    return render(request, "myapp/listing_detail.html", {"ads": ads})

def ad_detail(request, pk):
    ad = get_object_or_404(AD, pk=pk)
    return render(request, "myapp/ad_detail.html", {"ad": ad})

def order_ad(request, ad_id):
    ad = AD.objects.get(pk=ad_id)

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]

            subject = f"Замовлення на оголошення: {ad.title}"

            message = (
                f"Деталі замовлення:\n\n"
                f"Оголошення: {ad.title}\n"
                f"Ціна: {ad.price}\n\n"
                f"Ім’я: {name}\n"
                f"Email: {email}\n"
                f"Телефон: {phone}\n"
            )

            # адреси одержувачів — покупець і продавець
            recipients = [email]
            if hasattr(ad, "user") and ad.user.email:
                recipients.append(ad.user.email)

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)

            return render(request, "myapp/order_success.html", {"ad": ad})

    else:
        form = OrderForm()

    return render(request, "myapp/order_form.html", {"form": form, "ad": ad})


def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user_queryset = User.objects.filter(email=email)

            if user_queryset.exists():
                user = user_queryset.first()

                # 1. Створюємо тему та тіло листа
                subject = "Посилання для скидання пароля"

                # 2. Генеруємо унікальні частини посилання
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # 3. Створюємо повне посилання
                reset_link = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                message = f"Привіт, {user.username}!\n\n" \
                          f"Перейдіть за посиланням, щоб скинути ваш пароль:\n" \
                          f"{reset_link}\n\n" \
                          f"Якщо ви не робили цей запит, просто проігноруйте цей лист."

                # 4. Відправляємо лист
                send_mail(
                    subject,
                    message,
                    "noreply@mywebsite.com",
                    [user.email]
                )

            return redirect('password_reset_done')

    else:
        form = PasswordResetForm()

    return render(request, 'registration/password_reset_form.html', {'form': form})


def password_reset_done_view(request):
    """Сторінка, яка повідомляє, що інструкції відправлено."""
    return render(request, 'registration/password_reset_done.html')


def password_reset_confirm_view(request, uidb64=None, token=None):
    """Сторінка, яка перевіряє посилання і дозволяє скинути пароль."""
    # У реальному проекті тут буде логіка перевірки токена
    # і форма для введення нового пароля.
    # Для простоти ми просто покажемо, що посилання працює.
    context = {
        'uidb64': uidb64,
        'token': token
    }
    return render(request, 'registration/password_reset_confirm.html', context)