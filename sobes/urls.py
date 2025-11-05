from django.contrib import admin
from django.urls import path, include
from myapp import views # Імпорт views
# Явно імпортуємо функції скидання пароля, якщо вони у views.py
from myapp.views import password_reset, password_reset_done_view, password_reset_confirm_view 

# --- НЕОБХІДНІ ІМПОРТИ ДЛЯ МЕДІА ---
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
# -----------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('ad_create/', views.ad_create, name='ad_create'),
    path('listing/', views.listing_detail, name='listing_detail'),
    path('order/<int:ad_id>/', views.order_ad, name='order_ad'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('profile/', views.user_profile, name='profile'),
    path('ad/<slug:slug>/edit/', views.ad_edit, name='ad_edit'),
    path('ad/<slug:slug>/deactivate/', views.ad_deactivate, name='ad_deactivate'),

    path('ad/<slug:slug>/', views.ad_detail, name='ad_detail'),  # 🧠 <- оцей маршрут правильний
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('favorite-ads/', views.favorite_ads, name='favorite_ads'),
    path('toggle-favorite/<slug:slug>/', views.toggle_favorite, name='toggle_favorite'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-profile/', views.my_profile, name='my_profile'),
]


# --- КРИТИЧНО ВАЖЛИВИЙ БЛОК ДЛЯ МЕДІА-ФАЙЛІВ ---
if settings.DEBUG: # Перевірка, чи ввімкнено режим розробки
    # Додаємо URL-шаблон для роздачі медіа-файлів
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# -----------------------------------------------