from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import TaskViewSet, CategoryViewSet, RegisterView, UserDetailView

# Настройка маршрутов для вьюсетов
router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'categories', CategoryViewSet)

# Основные маршруты
urlpatterns = [
    path('', include(router.urls)),  # Включаем маршруты для вьюсетов
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Получение токена
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Обновление токена
    path('users/', UserDetailView.as_view(), name='user-detail')
]