import os
import django
import logging

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ToDoList.settings')  # Замените на ваше название проекта

# Инициализируем Django
django.setup()

from django.contrib.auth import get_user_model
from tasks.models import Category  # Теперь можно импортировать модель после инициализации

User = get_user_model()

# Создаем суперпользователя, если он еще не создан
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin'
    )
    logging.info("Superuser created")
else:
    logging.info("Superuser already exists")

# Создаем категории make, list и remind, если они еще не созданы
categories = ['make', 'list', 'remind']

for category_name in categories:
    if not Category.objects.filter(name=category_name).exists():
        Category.objects.create(name=category_name)
        logging.info(f"Category '{category_name}' created")
    else:
        logging.info(f"Category '{category_name}' already exists")