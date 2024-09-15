from django.shortcuts import render
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer  # создайте сериализатор для пользователя 
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Автоматически присваиваем пользователя из JWT токена или по ID."""
        user_id = self.request.data.get('user_id', None)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer.save(user=user)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Если user_id не передан, используем пользователя из JWT токена
            serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if User.objects.filter(username=username).exists():
            return Response({"detail": "Пользователь уже существует."}, status=status.HTTP_400_BAD_REQUEST)

        user = User(username=username, email=email, password=make_password(password))
        user.save()
        
        # Опционально: создайте токены для нового пользователя
        refresh = RefreshToken.for_user(user)
        return Response({
            "detail": "Пользователь успешно зарегистрирован!",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    
class UserDetailView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        username = request.query_params.get('username')

        if not user_id and not username:
            return Response({"error": "user_id или username обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if user_id:
                user = User.objects.get(id=user_id)
            elif username:
                user = User.objects.get(username=username)

            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)