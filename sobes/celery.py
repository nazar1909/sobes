
from celery import Celery
import os

# Встановлюємо змінну середовища DJANGO_SETTINGS_MODULE
# Щоб Celery знав, де шукати конфігурацію Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings')

# Створюємо екземпляр додатку Celery, використовуючи назву проекту 'sobes'
app = Celery('sobes')

# Використовуємо конфігурацію Django для Celery.
# Ключ конфігурації повинен починатися з 'CELERY_' (наприклад, CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматичне виявлення завдань у встановлених додатках Django
# Шукає файл tasks.py в кожному додатку (myapp/tasks.py, і т.д.)
app.autodiscover_tasks()
