import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

User = get_user_model()

# Проверьте, существует ли уже суперпользователь
if not User.objects.filter(is_superuser=True).exists():
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')

    print(f"Создаем администратора с именем {username}")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print("Администратор уже существует.")