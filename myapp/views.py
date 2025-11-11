from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm,inlineformset_factory,BaseAdImageInlineFormSet
from django.utils.html import escape
from django.contrib.auth import login
from django.urls import reverse
from .forms import AdForm,AdImageFormSet,AdImageForm
from django.contrib.auth.decorators import login_required
from .models import AD,Profile,AdImage
from django.core.mail import send_mail
from django.conf import settings
from .forms import OrderForm,PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden,HttpResponse,HttpResponseBadRequest
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from .forms import ProfileForm
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from .models import AD
import logging


# Create your views here.
def home(request):
    ads = AD.objects.all()
    return render(request, 'main/index.html',{'ads': ads})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # якщо успішно — перенаправлення

        # якщо форма невалідна — залишаємо користувача на сторінці
        # і Django сам передасть помилки у форму
        else:
            print(form.errors)  # для дебагу (потім можна видалити)
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def listing_detail(request,):
    ads = AD.objects.all()
    return render(request, "myapp/listing_detail.html", {"ads": ads})

def ad_detail(request, slug):
    ad = get_object_or_404(AD, slug=slug)
    #images=ad.image.all()
    return render(request, "myapp/ad_detail.html", {"ad": ad})
@login_required
def favorite_ads(request):

    ads = request.user.favorite_ads.all()  # через many-to-many
    return render(request, 'myapp/favorite_ads.html', {'ads': ads})

logger = logging.getLogger(__name__)

def order_ad(request, ad_id):
    ad = get_object_or_404(AD, pk=ad_id)

    if request.method == "POST":
        form = OrderForm(request.POST, user=request.user)
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

            recipients = [email]
            if getattr(ad, 'user', None) and ad.user.email:
                recipients.append(ad.user.email)

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
            except Exception as exc:
                logger.exception("Помилка відправки пошти: %s", exc)
                messages.warning(request, "Лист не вдалося відправити. Але замовлення надіслано.")

            return redirect('order_success')
        else:
            messages.error(request, "Перевірте правильність заповнення форми.")
    else:
        form = OrderForm(user=request.user)

    return render(request, "myapp/order_form.html", {"form": form, "ad": ad})

def order_success(request):
    return render(request, "myapp/order_success.html")


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


def password_reset_confirm_view(request, uidb64, token):
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, user)  # щоб не вилогінювало після зміни
                messages.success(request, "Пароль успішно змінено! Тепер ви можете увійти.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
    else:
        validlink = False
        form = None

    return render(request, 'registration/password_reset_confirm.html', {
        'form': form,
        'validlink': validlink
    })

@login_required
def user_profile(request):
    try:
        user_ads = AD.objects.filter(user=request.user).order_by('-date')
    except AttributeError:
        # Це просто заготовка на випадок, якщо поле називається інакше
        # Спробуйте 'user' або перевірте models.py
        user_ads = AD.objects.filter(user=request.user).order_by('-created_at')



    context = {
        'user_ads': user_ads
    }
    return render(request, 'myapp/profile.html', context)


@login_required
def ad_create(request):
    # ... (Оголошення AdImageFormSet тут або імпорт) ...

    if request.method == 'POST':
        form = AdForm(request.POST)

        # 1. Створюємо temp_formset
        temp_formset = AdImageFormSet(request.POST, request.FILES)

        # 2. ВАЛІДУЄМО ОБИДВА ОБ'ЄКТИ
        if form.is_valid() and temp_formset.is_valid():

            with transaction.atomic():
                ad = form.save(commit=False)
                ad.user = request.user
                ad.save()

                # 3. КРИТИЧНИЙ FIX: Встановлюємо інстанцію AD для ВЖЕ ВАЛІДОВАНОГО Formset
                temp_formset.instance = ad

                # 4. Зберігаємо ВЖЕ ВАЛІДОВАНИЙ Formset
                temp_formset.save()  # Це працює, бо cleaned_data існує!

                return redirect('ad_detail', slug=ad.slug)

        else:
            # Якщо валідація не пройшла, використовуємо temp_formset для відображення помилок
            formset = temp_formset  # Він вже містить дані та помилки

    else:
        # GET-запит
        form = AdForm()
        formset = AdImageFormSet(queryset=AdImage.objects.none())

    return render(request, 'myapp/ad_form.html', {'form': form, 'formset': formset})

@login_required
def ad_deactivate(request, slug):
    ad = get_object_or_404(AD, slug=slug)

    # Перевірка, що користувач є автором
    if request.user != ad.user:
        return HttpResponseForbidden("Ви не можете деактивувати чуже оголошення.")

    if request.method == 'POST':
        ad.delete() # Найпростіший спосіб "деактивувати"
        return redirect('profile') # Повертаємо на сторінку профілю

    # Якщо хтось зайшов GET-запитом, нічого не робимо
    return redirect('ad_detail', slug=ad.slug)


@login_required
def ad_edit(request, slug):
    ad = get_object_or_404(AD, slug=slug)

    # ❗ Тільки власник може редагувати
    if ad.user != request.user:
        return HttpResponseForbidden("Ви не можете редагувати це оголошення")

    # Підтягнемо всі фото, що належать цьому оголошенню
    existing_images = AdImage.objects.filter(ad=ad)

    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        formset = AdImageFormSet(request.POST, request.FILES, queryset=existing_images, instance=ad)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Оголошення оновлено ✅")
            return redirect('ad_detail', slug=ad.slug)
        else:
            messages.error(request, "Будь ласка, перевірте форму — є помилки.")
    else:
        form = AdForm(instance=ad)
        formset = AdImageFormSet(queryset=existing_images, instance=ad)

    return render(request, 'myapp/ad_form.html', {
        'form': form,
        'formset': formset,
        'is_edit': True,
        'ad': ad
    })
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

def validate_field(request):
    field = request.POST.get("field")
    value = request.POST.get("value")

    form = CustomUserCreationForm({field: value})
    form.is_valid()  # Запускаємо валідацію

    errors = form.errors.get(field)
    if errors:
        return JsonResponse({"valid": False, "errors": errors})
    return JsonResponse({"valid": True})

@login_required
def toggle_favorite(request, slug):
    ad = get_object_or_404(AD, slug=slug)
    user = request.user

    if user == ad.user:
        return JsonResponse({'success': False, 'error': 'Ви не можете вподобати власне оголошення'})

    if ad.favorites.filter(id=user.id).exists():
        ad.favorites.remove(user)
        is_favorite = False
    else:
        ad.favorites.add(user)
        is_favorite = True

    favorite_count = user.favorite_ads.count()

    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'favorite_count': favorite_count
    })
@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено ✅")
            return redirect('edit_profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'myapp/edit_profile.html', {'form': form})

@login_required
def my_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    user_ads = AD.objects.filter(user=request.user).order_by('-date')

    return render(request, 'myapp/my_profile.html', {
        'profile': profile,
        'ads': user_ads
    })

def search_ads(request):
    query = request.GET.get('q', '').strip()
    place = request.GET.get('place', '').strip()

    ads = AD.objects.all()

    # 🔍 Пошук за назвою або описом
    if query:
        ads = ads.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )

    # 📍 Фільтр за місцем
    if place and place.lower() != 'уся україна':
        ads = ads.filter(place__icontains=place)

    context = {
        'ads': ads,
        'query': query,
        'place': place,
    }

    return render(request, 'myapp/search_results.html', context)
def ad_suggestions(request):
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse([], safe=False)
    q = q[:200]
    ads = AD.objects.filter(Q(title__icontains=q) | Q(body__icontains=q)).values_list('title', flat=True)[:8]
    return JsonResponse(list(ads), safe=False)
def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    ads = AD.objects.filter(user=user).order_by('-date')
    profile = getattr(user, 'profile', None)

    return render(request, 'myapp/public_profile.html', {
        'profile_user': user,
        'profile': profile,
        'ads': ads,
    })