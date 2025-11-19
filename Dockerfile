# ---- BASE ----
FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Встановлення залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код
COPY . /app

# (опціонально) Виконати collectstatic ПІСЛЯ деплою вручну через Railway CLI
# RUN DJANGO_SETTINGS_MODULE=sobes.settings.production python manage.py collectstatic --noinput

EXPOSE 8000

# Gunicorn — production-ready WSGI сервер
CMD ["sh", "-c", "python manage.py wait_for_db && gunicorn sobes.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]