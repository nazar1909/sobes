import os
from celery import Celery
from django.conf import settings # Додайте цей імпорт

# Встановлюємо змінну середовища DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sobes.settings')

# 🛑 ФІНАЛЬНА ПЕРЕВІРКА ІЗОЛЯЦІЇ (ПЕРЕД ІНІЦІАЛІЗАЦІЄЮ)
# Це вирішує проблему, коли змінні середовища ОС перекривають Django settings.
if settings.DEBUG:
    # Примусово видаляємо змінні, які змушують Celery підключатися до RabbitMQ
    # Ми робимо це тільки в локальному режимі (DEBUG=True)
    if 'CELERY_BROKER_URL' in os.environ:
        del os.environ['CELERY_BROKER_URL']
    if 'RABBITMQ_HOST' in os.environ:
        del os.environ['RABBITMQ_HOST']
    # Це змушує Celery використовувати 'memory://' та EAGER режим з settings.py

# Створюємо екземпляр додатку Celery
# Якщо ми в режимі DEBUG, змінні RABBITMQ щойно були видалені, і Celery буде використовувати memory://
app = Celery('sobes')

# Використовуємо конфігурацію Django для Celery.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматичне виявлення завдань
app.autodiscover_tasks()