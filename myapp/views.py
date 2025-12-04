import json
from django.views.decorators.http import require_POST
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
from django.contrib.auth.forms import UserCreationForm, logger
from django import forms
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from .forms import ProfileForm
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q, Exists, OuterRef, Count,F,Subquery,Case, When, Value, CharField
from .models import AD,ChatRoom,ChatMessage,Notification
import logging
import os
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import AD
from .tasks import increment_ad_view

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


def get_paginated_data(request, queryset):
    PAGINATE_BY = 10
    paginator = Paginator(queryset, PAGINATE_BY)
    page_number = request.GET.get('page')

    try:
        # Спробувати отримати сторінку
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # Якщо сторінка не є числом (наприклад, ?page=abc), показати першу сторінку
        page_obj = paginator.page(1)
    except EmptyPage:
        # Якщо сторінка не існує (наприклад, ?page=999), показати останню сторінку
        page_obj = paginator.page(paginator.num_pages)

    return page_obj


def listing_detail(request):
    # 1. Базовий запит з анотаціями (лічильники лайків та чатів)
    ads_qs = AD.objects.annotate(
        favorites_count=Count('favorites', distinct=True),
        conversations_count=Count('chat_rooms', distinct=True)
    ).all().order_by('-date')

    # 2. Логіка "Режиму перегляду" (List/Grid)
    # Це обов'язково треба визначити до створення context
    view_mode = request.GET.get('view', 'list')
    if view_mode not in ['list', 'grid']:
        view_mode = 'list'

    # 3. [!!!] НОВА ЛОГІКА ЛАЙКІВ [!!!]
    # Створюємо список ID улюблених оголошень.
    # Це найнадійніший спосіб перевірки в шаблоні.
    favorite_ad_ids = []
    if request.user.is_authenticated:
        # Отримуємо чистий список чисел, наприклад: [1, 5, 12]
        favorite_ad_ids = list(request.user.favorite_ads.values_list('id', flat=True))

    # 4. Пагінація
    page_number = request.GET.get('page')
    paginator = Paginator(ads_qs, 10)  # 10 оголошень на сторінку
    page_obj = paginator.get_page(page_number)

    # 5. Формування контексту
    context = {
        'page_obj': page_obj,
        'view_mode': view_mode,
        'is_paginated': True,
        'favorite_ad_ids': favorite_ad_ids,  # <-- Передаємо список ID в шаблон
    }

    return render(request, 'myapp/listing_detail.html', context)


def ad_detail(request, slug):
    # 1. Отримуємо оголошення
    ad = get_object_or_404(AD, slug=slug)

    # 2. ОПТИМІЗОВАНИЙ ЛІЧИЛЬНИК (Celery)
    # Відправляємо задачу в Redis (це миттєво)
    increment_ad_view.delay(ad.id)

    # Візуально додаємо +1 для користувача, щоб він бачив, що перегляд зараховано.
    # Ми НЕ робимо тут ad.save(), щоб не блокувати базу.
    ad.views += 1

    # 3. ЛОГІКА КІМНАТИ ЧАТУ
    room_name = "chat_guest"
    if request.user.is_authenticated:
        # Унікальна кімната: ID оголошення + ID покупця
        room_name = f"{ad.id}-{request.user.id}"

    # 4. ЛОГІКА ЛАЙКІВ
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = ad.favorites.filter(id=request.user.id).exists()

    favorite_count = ad.favorites.count()

    # 5. ПЕРЕДАЄМО ДАНІ В ШАБЛОН
    return render(request, "myapp/ad_detail.html", {
        "ad": ad,
        "is_favorited": is_favorited,
        "favorite_count": favorite_count,

        # 🔥 ГОЛОВНЕ ВИПРАВЛЕННЯ:
        "room_name": room_name,
    })
@login_required
def favorite_ads(request):
    ads = request.user.favorite_ads.all().prefetch_related('images')  # ✅ Правильно
    return render(request, 'myapp/favorite_ads.html', {'ads': ads}) # ✅ Правильно передана змінна 'ads'

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

    favorite_count = ad.favorites.count()

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
            return redirect('my_profile')
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

@login_required
def chat_list(request):
    # 1. Підзапити (залишаємо як було)
    unread_subquery = ChatMessage.objects.filter(
        room=OuterRef('pk'),
        is_read=False
    ).exclude(sender=request.user)

    last_message_sq = ChatMessage.objects.filter(
        room=OuterRef('pk')
    ).order_by('-timestamp')

    last_message_content_sq = Subquery(
        last_message_sq.annotate(
            display_content=Case(
                When(
                    # (Немає тексту) І (Є файл)
                    (Q(content__isnull=True) | Q(content__exact='')) & Q(file__isnull=False),
                    then=Value('📷 Фото')
                ),
                default=F('content'),
                output_field=CharField()
            )
        ).values('display_content')[:1]
    )

    # 2. ГОЛОВНИЙ ЗАПИТ
    # 4. ГОЛОВНИЙ ЗАПИТ
    all_user_chats = ChatRoom.objects.filter(
        participants=request.user,
        messages__isnull=False  # <--- 1. ВІДСІЮЄМО ПУСТІ (немає записів у messages)
    ).distinct().select_related(  # <--- 2. ПРИБИРАЄМО ДУБЛІ (обов'язково!)
        'ad'
    ).prefetch_related(
        'participants__profile'
    ).annotate(
        has_unread_messages=Exists(unread_subquery),
        last_message_time=Subquery(last_message_sq.values('timestamp')[:1]),
        last_message_text=last_message_content_sq
    ).order_by(
        F('has_unread_messages').desc(),
        F('last_message_time').desc(nulls_last=True)
    )

    # 3. Розділення на списки (залишаємо як було)
    # 5. Розділення на прочитані/непрочитані
    unread_chats_list = []
    read_chats_list = []

    for chat in all_user_chats:
        # [!!!] ЗАЛІЗОБЕТОННИЙ ФІЛЬТР [!!!]
        # Якщо база не повернула час останнього повідомлення — значить повідомлень немає.
        # Ми просто пропускаємо цей крок циклу ("continue"), і чат не потрапляє в список.
        if chat.last_message_time is None:
            continue

        # Знаходимо співрозмовника (того, хто не я)
        others = [p for p in chat.participants.all() if p != request.user]
        chat.other_user = others[0] if others else None

        if chat.has_unread_messages:
            unread_chats_list.append(chat)
        else:
            read_chats_list.append(chat)

    context = {
        'unread_chats': unread_chats_list,
        'read_chats': read_chats_list,
    }

    return render(request, 'myapp/chat_list.html', context)
@login_required
def chat_detail(request, chat_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_id)

    # Перевірка доступу
    if request.user not in chat_room.participants.all():
        return HttpResponseForbidden("Ви не учасник цього чату")

    # Знаходимо співрозмовника (для логіки сповіщень)
    other_user = chat_room.participants.exclude(id=request.user.id).first()

    # =================================================================
    # 🔥 ЛОГІКА "ПРОЧИТАННЯ" (GET запит - коли відкрили сторінку)
    # =================================================================
    if request.method == 'GET':
        # 1. Позначаємо повідомлення в цьому чаті як прочитані.
        # Це автоматично зменшить лічильник unread_notifications_count у шапці.
        ChatMessage.objects.filter(
            room=chat_room,
            is_read=False
        ).exclude(
            sender=request.user
        ).update(is_read=True)

        # 2. Видаляємо старі записи Notification для цього чату/юзера.
        # Це потрібно для чистоти бази, щоб не накопичувати сміття.
        if other_user:
            Notification.objects.filter(
                recipient=request.user,
                sender=other_user,
                notification_type='message'
            ).delete()

    # =================================================================
    # 📨 ЛОГІКА ВІДПРАВКИ (POST запит)
    # =================================================================
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        attached_file = request.FILES.get('file', None)

        if content or attached_file:
            # 1. Зберігаємо в БД
            message = ChatMessage.objects.create(
                room=chat_room,
                sender=request.user,
                content=content,
                file=attached_file
            )

            # 2. Надсилаємо сповіщення через Channels (Redis)
            try:
                channel_layer = get_channel_layer()
                # Надсилаємо всім учасникам, крім себе
                if other_user:
                    group_name = f"user_{other_user.id}_notifications"

                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            'type': 'chat_notification',
                            'message': f"{request.user.username} написав вам",  # Для тоста
                            'sender': request.user.username,  # 🔥 ВАЖЛИВО: Для пошуку в списку чатів
                            'content': message.content if message.content else '📷 Фото',  # 🔥 ВАЖЛИВО: Текст прев'ю
                        }
                    )
            except Exception as e:
                print(f"⚠️ Помилка Channels: {e}")

            # 3. Відповідь для JavaScript (Fetch/AJAX)
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

            if is_ajax:
                file_url = message.file.url if message.file else None
                return JsonResponse({
                    'status': 'ok',
                    'content': message.content,
                    'timestamp': message.timestamp.strftime('%H:%M'),
                    'file_url': file_url,
                    'sender': request.user.username
                })

            # Фоллбек для звичайної форми
            return redirect('chat_detail', chat_id=chat_id)

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)

    # =================================================================
    # 🖥️ ВІДОБРАЖЕННЯ (GET)
    # =================================================================
    messages = chat_room.messages.select_related('sender__profile').all().order_by('timestamp')

    return render(request, 'myapp/chat_detail.html', {
        'chat_room': chat_room,
        'messages': messages,
        'other_user': other_user
    })

@login_required
def notifications_view(request):
    # 1. Отримуємо QuerySet (список сповіщень)
    notifications_qs = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    # 2. Маркуємо як прочитані (при вході на сторінку)
    notifications_qs.filter(is_read=False).update(is_read=True)

    # 3. Пагінація
    page_obj = get_paginated_data(request, notifications_qs)

    return render(request, 'myapp/notifications.html', {
        'page_obj': page_obj, # Передаємо об'єкт пагінації
    })


@login_required
def delete_notification(request, notif_id):
    """Видаляє сповіщення та перенаправляє назад."""
    # Перевіряємо, чи сповіщення належить користувачу
    notification = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notification.delete()
    return redirect('notifications')


@login_required
@require_GET
def get_new_messages(request, chat_id):
    # 1. Отримуємо ID останнього повідомлення, яке вже є на клієнті
    # Якщо параметр не передали, вважаємо, що це 0
    last_id = request.GET.get('last_id', 0)

    # 2. Шукаємо тільки НОВІ повідомлення в цьому чаті
    # id__gt означає "id greater than" (більше ніж)
    new_messages = ChatMessage.objects.filter(
        chat_room_id=chat_id,
        id__gt=last_id
    ).order_by('timestamp')

    results = []
    for msg in new_messages:
        # Визначаємо, чи це повідомлення поточного юзера
        is_me = msg.sender == request.user

        # Обробка файлу (якщо є)
        file_url = msg.file.url if msg.file else None
        file_name = msg.file.name.split('/')[-1] if msg.file else None

        # Обробка аватара (безпечно, якщо профілю чи фото немає)
        avatar_url = '/static/images/placeholder.png'
        bio = ''
        phone = ''

        if hasattr(msg.sender, 'profile'):
            if msg.sender.profile.image:
                avatar_url = msg.sender.profile.image.url
            bio = msg.sender.profile.bio or ''
            phone = msg.sender.profile.phone or ''

        # 3. Формуємо структуру даних для JavaScript
        results.append({
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%d.%m %H:%M'),  # Форматування часу
            'sender': msg.sender.username,
            'is_me': is_me,
            'avatar': avatar_url,
            'bio': bio,
            'phone': phone,
            'profile_url': f"/profile/{msg.sender.username}/",  # 👈 Перевірте свій URL для профілю
            'file_url': file_url,
            'file_name': file_name,
        })

    return JsonResponse({'status': 'ok', 'messages': results})


@login_required
def start_chat(request, ad_id):
    ad = get_object_or_404(AD, pk=ad_id)
    seller = ad.user
    buyer = request.user

    # 1. Захист від чату із самим собою
    if seller == buyer:
        messages.error(request, "Ви не можете почати чат із власним оголошенням.")
        return redirect('ad_detail', slug=ad.slug)

    # 2. Пошук або створення кімнати
    # Шукаємо чат, пов'язаний з цим оголошенням, де покупець є учасником.
    try:
        # Можна використовувати ChatRoom.objects.get, але filter() + first() більш гнучкий.
        # Шукаємо кімнату, де оголошення = ad, і в якій є обидва учасники.
        chat_room = ChatRoom.objects.filter(
            ad=ad,
            participants=buyer
        ).annotate(
             is_seller_present=Exists(ChatRoom.participants.through.objects.filter(
                 chatroom_id=OuterRef('pk'),
                 user=seller
             ))
        ).filter(is_seller_present=True).first()


        if not chat_room:
             # Створення нової кімнати, якщо не знайдено
             chat_room = ChatRoom.objects.create(ad=ad)
             chat_room.participants.add(seller, buyer)

    except Exception:
        # У разі будь-якої помилки (наприклад, проблем з participants), створити нову
        chat_room = ChatRoom.objects.create(ad=ad)
        chat_room.participants.add(seller, buyer)


    # 3. Перенаправляємо на деталі чату
    return redirect('chat_detail', chat_id=chat_room.id)