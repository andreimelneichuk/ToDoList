### Документация для API Django

#### Описание

Этот API предоставляет функционал для работы с задачами и категориями. Он включает в себя регистрацию пользователей, аутентификацию через JWT токены и управление задачами и категориями.

#### Конечные точки

1. **Создание задачи**
    - **URL:** `/api/tasks/`
    - **Метод:** `POST`
    - **Описание:** Создает новую задачу. При создании задачи автоматически присваивается пользователь из JWT токена или по ID.
    - **Тело запроса:**
        ```json
        {
            "title": "Task Title",
            "description": "Task Description",
            "due_date": "2024-09-30T12:00:00Z",
            "category": 1,
            "user_id": 1
        }
        ```
    - **Ответ:**
        - **Успешный ответ (201 Created):**
            ```json
            {
                "id": "e1d7b8f8d2a4238cba8e3e3d7bce56d8",
                "title": "Task Title",
                "description": "Task Description",
                "due_date": "2024-09-30T12:00:00Z",
                "category": 1,
                "user": 1,
                "is_completed": false
            }
            ```

2. **Получение всех задач**
    - **URL:** `/api/tasks/`
    - **Метод:** `GET`
    - **Описание:** Получает список всех задач.
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            [
                {
                    "id": "e1d7b8f8d2a4238cba8e3e3d7bce56d8",
                    "title": "Task Title",
                    "description": "Task Description",
                    "due_date": "2024-09-30T12:00:00Z",
                    "category": 1,
                    "user": 1,
                    "is_completed": false
                }
            ]
            ```

3. **Получение задачи по ID**
    - **URL:** `/api/tasks/{id}/`
    - **Метод:** `GET`
    - **Описание:** Получает информацию о задаче по её ID.
    - **Параметры пути:**
        - `id` (str): ID задачи.
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            {
                "id": "e1d7b8f8d2a4238cba8e3e3d7bce56d8",
                "title": "Task Title",
                "description": "Task Description",
                "due_date": "2024-09-30T12:00:00Z",
                "category": 1,
                "user": 1,
                "is_completed": false
            }
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "detail": "Not found."
            }
            ```

4. **Обновление задачи**
    - **URL:** `/api/tasks/{id}/`
    - **Метод:** `PUT`
    - **Описание:** Обновляет информацию о задаче по её ID.
    - **Параметры пути:**
        - `id` (str): ID задачи.
    - **Тело запроса:**
        ```json
        {
            "title": "Updated Task Title",
            "description": "Updated Task Description",
            "due_date": "2024-10-01T12:00:00Z",
            "category": 1,
            "user_id": 1,
            "is_completed": true
        }
        ```
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            {
                "id": "e1d7b8f8d2a4238cba8e3e3d7bce56d8",
                "title": "Updated Task Title",
                "description": "Updated Task Description",
                "due_date": "2024-10-01T12:00:00Z",
                "category": 1,
                "user": 1,
                "is_completed": true
            }
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "detail": "Not found."
            }
            ```

5. **Удаление задачи**
    - **URL:** `/api/tasks/{id}/`
    - **Метод:** `DELETE`
    - **Описание:** Удаляет задачу по её ID.
    - **Параметры пути:**
        - `id` (str): ID задачи.
    - **Ответ:**
        - **Успешный ответ (204 No Content):**
            ```json
            {}
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "detail": "Not found."
            }
            ```

6. **Создание категории**
    - **URL:** `/api/categories/`
    - **Метод:** `POST`
    - **Описание:** Создает новую категорию.
    - **Тело запроса:**
        ```json
        {
            "name": "Category Name"
        }
        ```
    - **Ответ:**
        - **Успешный ответ (201 Created):**
            ```json
            {
                "id": 1,
                "name": "Category Name"
            }
            ```

7. **Получение всех категорий**
    - **URL:** `/api/categories/`
    - **Метод:** `GET`
    - **Описание:** Получает список всех категорий.
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            [
                {
                    "id": 1,
                    "name": "Category Name"
                }
            ]
            ```

8. **Получение категории по ID**
    - **URL:** `/api/categories/{id}/`
    - **Метод:** `GET`
    - **Описание:** Получает информацию о категории по её ID.
    - **Параметры пути:**
        - `id` (int): ID категории.
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            {
                "id": 1,
                "name": "Category Name"
            }
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "detail": "Not found."
            }
            ```

9. **Регистрация пользователя**
    - **URL:** `/api/register/`
    - **Метод:** `POST`
    - **Описание:** Регистрация нового пользователя.
    - **Тело запроса:**
        ```json
        {
            "username": "newuser",
            "password": "password123",
            "email": "newuser@example.com"
        }
        ```
    - **Ответ:**
        - **Успешный ответ (201 Created):**
            ```json
            {
                "detail": "Пользователь успешно зарегистрирован!",
                "refresh": "refresh_token",
                "access": "access_token"
            }
            ```
        - **Ошибка (400 Bad Request):**
            ```json
            {
                "detail": "Пользователь уже существует."
            }
            ```

10. **Получение информации о пользователе**
    - **URL:** `/api/users/`
    - **Метод:** `GET`
    - **Описание:** Получает информацию о пользователе по ID или имени пользователя.
    - **Параметры запроса:**
        - `user_id` (int): ID пользователя.
        - `username` (str): Имя пользователя.
    - **Ответ:**
        - **Успешный ответ (200 OK):**
            ```json
            {
                "id": 1,
                "username": "existinguser",
                "email": "existinguser@example.com"
            }
            ```
        - **Ошибка (400 Bad Request):**
            ```json
            {
                "error": "user_id или username обязательны"
            }
            ```
        - **Ошибка (404 Not Found):**
            ```json
            {
                "error": "User not found"
            }
            ```

#### Аутентификация и авторизация

- Для доступа к защищенным ресурсам требуется JWT токен. Получите токен с помощью `/api/token/` и используйте его в заголовках запросов как `Authorization: Bearer <token>`.

#### Обработка задач с помощью Celery

- **Функция:** `send_due_date_notifications`
  - **Описание:** Проверяет задачи с истекшим сроком выполнения и отправляет уведомления.
