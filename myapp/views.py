from django.shortcuts import render,redirect,get_object_or_404
from .forms import CustomUserCreationForm
import re
from django.contrib.auth import login
from .forms import AdForm
from django.contrib.auth.decorators import login_required
from .models import AD
from django.core.mail import send_mail
from django.conf import settings
from .forms import OrderForm

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