"""
URL configuration for sobes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from myapp import views
from django.conf.urls.static import static
from django.conf import settings
from myapp.views import password_reset,password_reset_done_view,password_reset_confirm_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/',views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ad_create/', views.ad_create, name='ad_create'),
    path("listing/", views.listing_detail, name="listing_detail"),
    path("listing/<int:pk>/", views.ad_detail, name="ad_detail"),
    path('order/<int:ad_id>/', views.order_ad, name='order_ad'),
    path('password-reset/', password_reset, name='password_reset'),
    path('password-reset/done/', password_reset_done_view, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
