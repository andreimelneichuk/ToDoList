### Документация для API FastAPI

#### Описание

Этот API предоставляет возможности для создания, получения, обновления и удаления комментариев, связанных с задачами. Комментарии хранятся в Redis и информация о задачах извлекается из основного бэкенда, работающего на Django.

#### Конечные точки

1. **Создание комментария**
    - **URL:** `/comments/`
    - **Метод:** `POST`
    - **Описание:** Создает новый комментарий для задачи. Проверяет существование задачи в основном бэкенде и сохраняет комментарий в Redis.
    - **Тело запроса:**
        ```json
        {
            "task_id": 1,
            "user_id": 123,
            "content": "This is a comment"
        }
        ```
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            {
                "message": "Comment created"
            }
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "detail": "Task not found"
            }
            ```

2. **Получение комментариев для задачи**
    - **URL:** `/tasks/{task_id}/comments/`
    - **Метод:** `GET`
    - **Описание:** Получает все комментарии для указанной задачи из Redis.
    - **Параметры пути:**
        - `task_id` (int): ID задачи, для которой нужно получить комментарии.
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            {
                "1": "This is a comment",
                "2": "Another comment"
            }
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "detail": "No comments found"
            }
            ```

3. **Обновление комментария**
    - **URL:** `/comments/{task_id}/{user_id}`
    - **Метод:** `PUT`
    - **Описание:** Обновляет текст комментария в Redis по ID задачи и ID пользователя.
    - **Параметры пути:**
        - `task_id` (int): ID задачи, к которой относится комментарий.
        - `user_id` (int): ID пользователя, который добавил комментарий.
    - **Тело запроса:**
        ```json
        {
            "content": "Updated comment"
        }
        ```
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            {
                "message": "Comment updated"
            }
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "detail": "Comment not found"
            }
            ```

4. **Удаление комментария**
    - **URL:** `/comments/{task_id}/{user_id}`
    - **Метод:** `DELETE`
    - **Описание:** Удаляет комментарий из Redis по ID задачи и ID пользователя.
    - **Параметры пути:**
        - `task_id` (int): ID задачи, к которой относится комментарий.
        - `user_id` (int): ID пользователя, который добавил комментарий.
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            {
                "message": "Comment deleted"
            }
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "detail": "Comment not found"
            }
            ```
