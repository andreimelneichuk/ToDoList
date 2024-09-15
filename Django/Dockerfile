# Используем официальный образ Python
FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Выполняем миграции и создаем суперпользователя при запуске контейнера
CMD bash -c "python manage.py makemigrations && \
    python manage.py migrate && \
    echo \"from django.contrib.auth import get_user_model; \
          User = get_user_model(); \
          User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists() or \
          User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')\" | python manage.py shell && \
    python manage.py runserver 0.0.0.0:8000"