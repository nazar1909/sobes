"""
WSGI config for sobes project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import django
from django.core.wsgi import get_wsgi_application
from django.conf import settings # Імпортуємо налаштування
import cloudinary

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings.production')
django.setup()
application = get_wsgi_application()


try:
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
            secure=True
        )
        print("✅ Cloudinary initialized in WSGI")
except Exception as e:
    print(f"⚠️ Cloudinary init failed: {e}")