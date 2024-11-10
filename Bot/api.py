import logging
import aiohttp
from config import DJANGO_API_URL, FASTAPI_URL, get_django_credentials, get_django_tockens, set_django_tokens
from aiogram_dialog import DialogManager
import requests
from login import start_login_dialog
ACCESS_TOKEN, REFRESH_TOKEN = get_django_tockens()

async def refresh_tokens():
    try:
        response = await aiohttp.ClientSession().post(
            f"{DJANGO_API_URL}token/refresh/",
            json={"refresh": REFRESH_TOKEN}
        )
        if response.status == 200:
            tokens = await response.json()
            set_django_tokens(tokens['access'], tokens['refresh'])
            logging.info("Токены обновлены успешно.")
        else:
            logging.error(f"Ошибка обновления токенов: {response.status}")
            set_django_tokens(None, None)
    except Exception as e:
        logging.error(f"Ошибка при обновлении токенов: {e}")
        set_django_tokens(None, None)

    if ACCESS_TOKEN is None:
        try:
            async with aiohttp.ClientSession() as session:
                DJANGO_USERNAME, DJANGO_PASSWORD = get_django_credentials()
                async with session.post(f"{DJANGO_API_URL}token/", json={"username": DJANGO_USERNAME, "password": DJANGO_PASSWORD}) as response:
                    if response.status == 200:
                        tokens = await response.json()
                        set_django_tokens(tokens['access'], tokens['refresh'])
                    else:
                        logging.error(f"Ошибка получения токенов: {response.status}")
        except Exception as e:
            logging.error(f"Ошибка получения токенов: {e}")
    return ACCESS_TOKEN

async def get_jwt_token():
    global ACCESS_TOKEN, REFRESH_TOKEN
    if get_django_credentials() == (None, None):
        start_login_dialog()
    if ACCESS_TOKEN is None:
        try:
            async with aiohttp.ClientSession() as session:
                DJANGO_USERNAME , DJANGO_PASSWORD = get_django_credentials()
                async with session.post(
                    f"{DJANGO_API_URL}token/",
                    json={"username": DJANGO_USERNAME, "password": DJANGO_PASSWORD}
                ) as response:
                    if response.status == 200:
                        tokens = await response.json()
                        set_django_tokens(tokens['access'], tokens['refresh'])
                        logging.info("Токены получены успешно.")
                    else:
                        logging.error(f"Ошибка получения токенов: {response.status}")
                        set_django_tokens(None, None)
        except Exception as e:
            logging.error(f"Ошибка при получении токенов: {e}")
            set_django_tokens(None, None)

    if ACCESS_TOKEN:
        logging.info("Проверяем токены.")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{DJANGO_API_URL}tasks/",
                    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
                ) as response:
                    if response.status == 401:
                        try:
                            async with session.post(
                                f"{DJANGO_API_URL}token/refresh/",
                                json={"refresh": REFRESH_TOKEN}
                            ) as response:
                                if response.status == 200:
                                    tokens = await response.json()
                                    set_django_tokens(tokens['access'], tokens['refresh'])
                                    logging.info("Токены обновлены успешно.")
                                else:
                                    logging.error(f"Ошибка обновления токенов: {response.status}")
                                    ACCESS_TOKEN = None
                        except Exception as e:
                            logging.error(f"Ошибка при обновлении токенов: {e}")
                            set_django_tokens(None, None)
        except Exception as e:
            logging.error(f"Ошибка при проверке токена: {e}")
            set_django_tokens(None, None)

    return ACCESS_TOKEN


async def get_user_id_by_username(username):
    token = await get_jwt_token()
    if not token:
        start_login_dialog(DialogManager)
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{DJANGO_API_URL}users/", params={"username": username}, headers=headers)
        if response.status_code == 200:
            users = response.json()
            if users:
                return users["id"]  # Предполагаем, что первый пользователь - это нужный
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка получения ID пользователя: {e}")
        return None

async def get_category_by_name(category_name):
    token = await get_jwt_token()
    if not token:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{DJANGO_API_URL}categories/", params={"name": category_name}, headers={"Authorization": f"Bearer {token}"}) as response:
                if response.status == 200:
                    categories = await response.json()
                    return categories[0]["id"] if categories else None
    except Exception as e:
        logging.error(f"Ошибка проверки категории: {e}")
    return None

async def get_tasks(user_id):
    token = await get_jwt_token()
    if not token:
        return []
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{DJANGO_API_URL}tasks/", params={'user_id': user_id}, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка получения задач: {e}")
        return []


async def register_user(dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    username = data["username"]
    password = data["password"]
    email = data["email"]

    logging.info(f"Регистрация пользователя {username}")

    url = f"{DJANGO_API_URL}register/"
    payload = {
        "username": username,
        "password": password,
        "email": email
    }

    logging.info(f"URL для регистрации: {url}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            

            if response.status == 201:
                global ACCESS_TOKEN, REFRESH_TOKEN
                ACCESS_TOKEN = result.get('access')
                REFRESH_TOKEN = result.get('refresh')
                logging.info(f"Ответ от сервера: {result}")
                await bot.send_message(
                    dialog_manager.event.from_user.id, "Регистрация успешна!"
                )
                # Обновляем глобальные переменные
                DJANGO_USERNAME = data["username"]
                DJANGO_PASSWORD = data["password"]
            else:
                error_message = result.get('detail', 'Неизвестная ошибка')
                await bot.send_message(
                    dialog_manager.event.from_user.id, f"Ошибка регистрации: {error_message}"
                )

    await dialog_manager.done()  # Завершение диалога

# Получение комментариев с использованием токена
async def get_comments(task_id):
    token = await get_jwt_token()
    if not token:
        return []
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{FASTAPI_URL}tasks/{task_id}/comments/", headers=headers)
        
        if response.status_code == 200:
            return response.json().get('comments', [])
        else:
            logging.error(f"Ошибка при получении комментариев: {response.status_code} {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка получения комментариев: {e}")
        return []

# Добавление комментария с использованием токена
async def add_comment(task_id, comment, user_id):
    token = await get_jwt_token()
    if not token:
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "task_id": task_id,
            "user_id": user_id,
            "content": comment  # Название поля должно соответствовать модели Comment в FastAPI
        }
        
        response = requests.post(FASTAPI_URL, json=payload, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            logging.error(f"Ошибка при добавлении комментария: {response.status_code} {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка добавления комментария: {e}")
        return False