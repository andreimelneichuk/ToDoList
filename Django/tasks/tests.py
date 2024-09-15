from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Task, Category
from rest_framework_simplejwt.tokens import RefreshToken

# Функция для получения JWT токена для пользователя
def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

class TaskTests(APITestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Создаем категорию для задач
        self.category = Category.objects.create(name='Work')

        # Получаем токен и устанавливаем его в заголовки
        self.token = get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_task(self):
        url = reverse('task-list')
        data = {
            "title": "Test Task",
            "description": "Test task description",
            "due_date": "2024-12-31T12:00:00Z",
            "category": self.category.id,
            "is_completed": False,
            "user": self.user.id,
        }

        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'Test Task')

    def test_get_task_list(self):
        Task.objects.create(
            title="Test Task", 
            description="Test task description", 
            due_date="2024-12-31T12:00:00Z", 
            category=self.category, 
            user=self.user,
            is_completed=False
        )
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_task(self):
        task = Task.objects.create(
            title="Test Task", 
            description="Test task description", 
            due_date="2024-12-31T12:00:00Z", 
            category=self.category, 
            user=self.user,
            is_completed=False
        )
        url = reverse('task-detail', args=[task.id])
        data = {
            "title": "Updated Task",
            "description": "Updated task description",
            "due_date": "2024-12-31T12:00:00Z",
            "category": self.category.id,
            "is_completed": True,
            "user": self.user.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Task')
        self.assertEqual(task.is_completed, True)

    def test_delete_task(self):
        task = Task.objects.create(
            title="Test Task", 
            description="Test task description", 
            due_date="2024-12-31T12:00:00Z", 
            category=self.category, 
            user=self.user,
            is_completed=False
        )
        url = reverse('task-detail', args=[task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

class CategoryTests(APITestCase):

    def setUp(self):
        # Удаление всех существующих категорий перед началом тестов
        Category.objects.all().delete()
        
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuserr', password='testpass')
        
        # Получаем токен и устанавливаем его в заголовки
        self.token = get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_category(self):
        url = reverse('category-list')
        data = {"name": "Personal"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get().name, 'Personal')

    def test_get_category_list(self):
        Category.objects.create(name='Work')
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_category(self):
        category = Category.objects.create(name='Work')
        url = reverse('category-detail', args=[category.id])
        data = {"name": "Updated Work"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Work')

    def test_delete_category(self):
        category = Category.objects.create(name='Work')
        url = reverse('category-detail', args=[category.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)