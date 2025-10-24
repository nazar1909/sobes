# /wait_for_db_app/management/commands/wait_for_db.py

import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django-команда, щоб чекати на готовність бази даних"""

    def handle(self, *args, **options):
        self.stdout.write('Чекаємо на базу даних...')

        db_ready = False
        while not db_ready:
            try:
                # Спробувати отримати з'єднання 'default' і виконати запит
                db_conn = connections['default']
                db_conn.cursor()

                # Якщо .cursor() не видав помилку, база готова
                db_ready = True

            except OperationalError:
                self.stdout.write('База даних недоступна, чекаємо 1 секунду...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('База даних готова!'))