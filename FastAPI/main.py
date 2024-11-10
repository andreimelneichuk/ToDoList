from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import redis
import requests
from typing import List, Optional

app = FastAPI()

# Настройка Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Конфигурация основного бэкенда
MAIN_BACKEND_URL = "http://django:8000/api/"

# Модель комментария
class Comment(BaseModel):
    task_id: str
    user_id: int
    content: str

# Модель обновления комментария
class CommentUpdate(BaseModel):
    content: str

# Вспомогательная функция для проверки токена и запросов к Django API
def check_django_task(task_id: str, jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{MAIN_BACKEND_URL}tasks/{task_id}", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Task not found")
    return response.json()

# Создание комментария
@app.post("/comments/")
async def create_comment(comment: Comment, Authorization: Optional[str] = Header(None)):
    # Проверяем наличие токена
    if not Authorization:
        raise HTTPException(status_code=403, detail="Authorization token is missing")

    jwt_token = Authorization.split(" ")[1]  # Извлекаем токен из "Bearer <token>"

    # Проверяем существование задачи через Django API
    task_data = check_django_task(comment.task_id, jwt_token)

    # Сохраняем комментарий в Redis
    redis_client.hset(f"task:{comment.task_id}:comments", comment.user_id, comment.content)
    return {"message": "Comment created", "task_data": task_data}

# Получение комментариев для задачи
@app.get("/tasks/{task_id}/comments/")
async def get_comments(task_id: str, Authorization: Optional[str] = Header(None)):
    # Проверяем наличие токена
    if not Authorization:
        raise HTTPException(status_code=403, detail="Authorization token is missing")

    jwt_token = Authorization.split(" ")[1]  # Извлекаем токен из "Bearer <token>"

    # Проверяем задачу через Django API
    task_data = check_django_task(task_id, jwt_token)

    # Получаем комментарии из Redis
    comments = redis_client.hgetall(f"task:{task_id}:comments")
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")
    
    result = {int(k): v.decode("utf-8") for k, v in comments.items()}
    return {"task_data": task_data, "comments": result}

# Обновление комментария
@app.put("/comments/{task_id}/{user_id}")
async def update_comment(task_id: int, user_id: int, comment_update: CommentUpdate, Authorization: Optional[str] = Header(None)):
    # Проверяем наличие токена
    if not Authorization:
        raise HTTPException(status_code=403, detail="Authorization token is missing")

    jwt_token = Authorization.split(" ")[1]  # Извлекаем токен из "Bearer <token>"

    # Проверяем существование задачи через Django API
    check_django_task(task_id, jwt_token)

    # Проверяем существование комментария
    if not redis_client.hexists(f"task:{task_id}:comments", user_id):
        raise HTTPException(status_code=404, detail="Comment not found")

    # Обновляем комментарий в Redis
    redis_client.hset(f"task:{task_id}:comments", user_id, comment_update.content)
    return {"message": "Comment updated"}

# Удаление комментария
@app.delete("/comments/{task_id}/{user_id}")
async def delete_comment(task_id: int, user_id: int, Authorization: Optional[str] = Header(None)):
    # Проверяем наличие токена
    if not Authorization:
        raise HTTPException(status_code=403, detail="Authorization token is missing")

    jwt_token = Authorization.split(" ")[1]  # Извлекаем токен из "Bearer <token>"

    # Проверяем существование задачи через Django API
    check_django_task(task_id, jwt_token)

    # Проверка существования комментария
    if not redis_client.hexists(f"task:{task_id}:comments", user_id):
        raise HTTPException(status_code=404, detail="Comment not found")

    # Удаление комментария
    redis_client.hdel(f"task:{task_id}:comments", user_id)
    return {"message": "Comment deleted"}