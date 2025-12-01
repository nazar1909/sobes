from celery import shared_task
import time

@shared_task
def test_task():
    # Якийсь код вашого старого завдання
    print("Виконую test_task...")
    pass

# ДОДАЙТЕ ЦЕЙ КОД В ЦЕЙ Ж ФАЙЛ
@shared_task
def add(x, y):
    print(f"Отримав завдання: {x} + {y}")
    time.sleep(5)  # Імітуємо 5 секунд роботи
    result = x + y
    print(f"Завдання виконано: {result}")
    return result

@shared_task
def increment_ad_view(ad_id):
    AD.objects.filter(pk=ad_id).update(views=F('views') + 1)