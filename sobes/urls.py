from django.contrib import admin
from django.urls import path, include
from myapp import views # Імпорт views
# Явно імпортуємо функції скидання пароля, якщо вони у views.py
from myapp.views import password_reset, password_reset_done_view, password_reset_confirm_view, chat_list

# --- НЕОБХІДНІ ІМПОРТИ ДЛЯ МЕДІА ---
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
# -----------------------------------
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('ad_create/', views.ad_create, name='ad_create'),
    path('listing/', views.listing_detail, name='listing_detail'),

    path('order/<int:ad_id>/', views.order_ad, name='order_ad'),
    path('order/success/', views.order_success, name='order_success'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('profile/', views.user_profile, name='profile'),
    path('ad/<slug:slug>/edit/', views.ad_edit, name='ad_edit'),
    path('ad/<slug:slug>/deactivate/', views.ad_deactivate, name='ad_deactivate'),
    path('ajax/suggestions/', views.ad_suggestions, name='ad_suggestions'),
    path('my-chats/', views.chat_list, name='chat_list'),
    path('ad/<slug:slug>/', views.ad_detail, name='ad_detail'),  # 🧠 <- оцей маршрут правильний
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('favorite-ads/', views.favorite_ads, name='favorite_ads'),
    path('toggle-favorite/<slug:slug>/', views.toggle_favorite, name='toggle_favorite'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('search/', views.search_ads, name='search_ads'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/', include('myapp.api.urls')),
    path('api/v1/', include('myapp.api.urls')),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path('my-chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/delete/<int:notif_id>/', views.delete_notification, name='delete_notification'),
    path('ad/<int:ad_id>/start-chat/', views.start_chat, name='start_chat'),
]

schema_view = get_schema_view(
   openapi.Info(
      title="SOBES API",
      default_version='v1',
      description="Документація API для SOBES",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)
urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
if settings.DEBUG:
    # Додаємо роздачу МЕДІА (картинки користувачів)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Додаємо роздачу СТАТИКИ (ваш CSS, JS)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
# -----------------------------------------------