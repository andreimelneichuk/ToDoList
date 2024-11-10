# Используем официальный образ Python
FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD bash -c "python manage.py makemigrations && \
    python manage.py migrate && \
    python create_admin.py \
    python manage.py runserver 0.0.0.0:8000"