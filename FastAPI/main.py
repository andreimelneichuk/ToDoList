from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import redis
import requests
from typing import List, Optional

app = FastAPI()

# Настройка Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Конфигурация основного бэкенда
MAIN_BACKEND_URL = "http://django/api/"

# Модель комментария
class Comment(BaseModel):
    task_id: int
    user_id: int
    content: str

# Модель обновления комментария
class CommentUpdate(BaseModel):
    content: str

# Создание комментария
@app.post("/comments/")
async def create_comment(comment: Comment):
    # Получаем информацию о задаче с основного бэкенда
    response = requests.get(f"{MAIN_BACKEND_URL}/{comment.task_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Task not found")

    # Сохранение комментария в Redis (в данном примере без использования БД)
    redis_client.hset(f"task:{comment.task_id}:comments", comment.user_id, comment.content)
    return {"message": "Comment created"}

# Получение комментариев для задачи
@app.get("/tasks/{task_id}/comments/")
async def get_comments(task_id: int):
    comments = redis_client.hgetall(f"task:{task_id}:comments")
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")
    
    # Преобразование данных для ответа
    result = {int(k): v.decode("utf-8") for k, v in comments.items()}
    return result

# Обновление комментария
@app.put("/comments/{task_id}/{user_id}")
async def update_comment(task_id: int, user_id: int, comment_update: CommentUpdate):
    # Проверяем существование комментария
    if not redis_client.hexists(f"task:{task_id}:comments", user_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Обновляем комментарий в Redis
    redis_client.hset(f"task:{task_id}:comments", user_id, comment_update.content)
    return {"message": "Comment updated"}

# Удаление комментария
@app.delete("/comments/{task_id}/{user_id}")
async def delete_comment(task_id: int, user_id: int):
    # Проверка существования комментария
    if not redis_client.hexists(f"task:{task_id}:comments", user_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Удаление комментария
    redis_client.hdel(f"task:{task_id}:comments", user_id)
    return {"message": "Comment deleted"}