import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import Dialog, DialogRegistry, Window, StartMode
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import TextInput
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram_dialog.manager.manager import DialogManager
import logging
import aiohttp

# Базовые настройки бота
API_TOKEN = '7278441677:AAE6o6B50DTEQkbvDmpFD7sHSJBO3k2jx2w'
DJANGO_API_URL = "http://django:8000/api/"
FASTAPI_URL = "http://fastapi:8001/comments/"

# Логин и пароль для получения токена
DJANGO_USERNAME = "my_username"
DJANGO_PASSWORD = "my_password"

# Инициализация бота и диспетчера
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
registry = DialogRegistry(dp)

# Функция для получения JWT токена
# Глобальные переменные для хранения токенов
ACCESS_TOKEN = None
REFRESH_TOKEN = None

async def refresh_tokens():
    global ACCESS_TOKEN, REFRESH_TOKEN
    try:
        response = await aiohttp.ClientSession().post(
            f"{DJANGO_API_URL}token/refresh/",
            json={"refresh": REFRESH_TOKEN}
        )
        if response.status == 200:
            tokens = await response.json()
            ACCESS_TOKEN = tokens['access']
            REFRESH_TOKEN = tokens['refresh']
            logging.info("Токены обновлены успешно.")
        else:
            logging.error(f"Ошибка обновления токенов: {response.status}")
            ACCESS_TOKEN = None
            REFRESH_TOKEN = None
    except Exception as e:
        logging.error(f"Ошибка при обновлении токенов: {e}")
        ACCESS_TOKEN = None
        REFRESH_TOKEN = None

async def get_jwt_token():
    global ACCESS_TOKEN, REFRESH_TOKEN

    if ACCESS_TOKEN is None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{DJANGO_API_URL}token/",
                    json={"username": DJANGO_USERNAME, "password": DJANGO_PASSWORD}
                ) as response:
                    if response.status == 200:
                        tokens = await response.json()
                        ACCESS_TOKEN = tokens['access']
                        REFRESH_TOKEN = tokens['refresh']
                        logging.info("Токены получены успешно.")
                    else:
                        logging.error(f"Ошибка получения токенов: {response.status}")
                        ACCESS_TOKEN = None
        except Exception as e:
            logging.error(f"Ошибка при получении токенов: {e}")
            ACCESS_TOKEN = None

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
                                    ACCESS_TOKEN = tokens['access']
                                    REFRESH_TOKEN = tokens['refresh']
                                    logging.info("Токены обновлены успешно.")
                                else:
                                    logging.error(f"Ошибка обновления токенов: {response.status}")
                                    ACCESS_TOKEN = None
                        except Exception as e:
                            logging.error(f"Ошибка при обновлении токенов: {e}")
                            ACCESS_TOKEN = None
        except Exception as e:
            logging.error(f"Ошибка при проверке токена: {e}")
            ACCESS_TOKEN = None

    return ACCESS_TOKEN

async def get_user_id_by_username(username):
    token = await get_jwt_token()
    if not token:
        return None
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

# Получение задач пользователя с токеном
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

# Получение комментариев с токеном
async def get_comments(task_id):
    token = await get_jwt_token()
    if not token:
        return []
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{FASTAPI_URL}{task_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка получения комментариев: {e}")
        return []

# Добавление комментария с токеном
async def add_comment(task_id, comment, user_id):
    token = await get_jwt_token()
    if not token:
        return False
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(FASTAPI_URL, json={
            "task_id": task_id,
            "comment": comment,
            "user_id": user_id
        }, headers=headers)
        return response.status_code == 201
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка добавления комментария: {e}")
        return False

async def get_category_by_name(category_name):
    token = await get_jwt_token()
    if not token:
        return None
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{DJANGO_API_URL}categories/", params={"name": category_name}, headers=headers)
        if response.status_code == 200:
            categories = response.json()
            if categories:
                return categories[0]["id"]
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка проверки категории: {e}")
        return None
    

class CommentDialog(StatesGroup):
    waiting_for_task_id = State()
    waiting_for_comment = State()

# Стартовая команда
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Привет! Я помогу тебе управлять твоими задачами. Используй /tasks для просмотра задач.")



# Определение группы состояний
class RegistrationDialog(StatesGroup):
    start = State()
    ask_password = State()
    ask_email = State()

# Диалоги
async def get_name(message: types.Message, windget,  dialog_manager: DialogManager, input_value:str):
    dialog_manager.current_context().dialog_data["username"] = input_value
    await dialog_manager.switch_to(RegistrationDialog.ask_password)

async def get_password(message: types.Message,widget, dialog_manager: DialogManager,input_value: str):
    dialog_manager.current_context().dialog_data["password"] = input_value
    await dialog_manager.switch_to(RegistrationDialog.ask_email)

async def get_email(message: types.Message, widget, dialog_manager: DialogManager, input_value: str):
    dialog_manager.current_context().dialog_data["email"] = input_value
    await register_user(dialog_manager)

# Функция регистрации
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

# Диалоги для добавления задачи
reg_dialog = Dialog(
    Window(
        Const("Введите ваше имя пользователя:"),
        TextInput(id='username', on_success=get_name),
        state=RegistrationDialog.start
    ),
    Window(
        Const("Введите ваш пароль:"),
        TextInput(id='password', on_success=get_password),
        state=RegistrationDialog.ask_password
    ),
    Window(
        Const("Введите ваш email:"),
        TextInput(id='email', on_success=get_email),
        state=RegistrationDialog.ask_email
    ),
)

# Регистрируем диалоги в DialogRegistry
registry.register(reg_dialog)

# Стартовая команда для начала диалога
@dp.message_handler(commands=["register"])
async def start_dialog(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(RegistrationDialog.start, mode=StartMode.RESET_STACK)

# Просмотр задач
@dp.message_handler(commands=['tasks'])
async def list_tasks(message: types.Message):
    tasks = await get_tasks(message.from_user.id)
    if tasks:
        task_list = "\n".join([f"{task['title']} (Категория: {task['category']}, Создано: {task['due_date']})" for task in tasks])
        await message.answer(f"Ваши задачи:\n{task_list}")
    else:
        await message.answer("У вас нет задач.")

# Диалоговое состояние для добавления задачи
class TaskDialog(StatesGroup):
    waiting_for_task_title = State()
    waiting_for_task_description = State()
    waiting_for_task_due_date = State()
    waiting_for_task_category = State()
    waiting_for_task_completion = State()

# Обработчик команды /add_task
@dp.message_handler(commands=['add_task'])
async def add_task(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(TaskDialog.waiting_for_task_title, mode=StartMode.RESET_STACK)
# Обработка завершения ввода названия задачи
async def process_task_title(message: types.Message, widget, dialog_manager: DialogManager, input_value: str):
    dialog_manager.current_context().dialog_data["task_title"] = input_value
    logging.info(f"Добавление задачи на сервер Django:")
    
    # Переход к состоянию ввода описания задачи
    await dialog_manager.switch_to(TaskDialog.waiting_for_task_description)

# Обработка завершения ввода описания задачи
async def process_task_description(message: types.Message, widget, dialog_manager: DialogManager, input_value: str):
    dialog_manager.current_context().dialog_data["task_description"] = input_value
    logging.info(f"Добавление задачи на сервер Django:")
    
    # Переход к состоянию ввода категории задачи
    await dialog_manager.switch_to(TaskDialog.waiting_for_task_category)

async def process_task_category(message: types.Message, widget, dialog_manager: DialogManager, input_value: str):
    logging.info(f"Добавление задачи на сервер Django:")

    # Проверяем существование категории
    category_id = await get_category_by_name(input_value)
    if not category_id:
        await dialog_manager.event.answer("Категория не найдена. Убедитесь, что категория существует.")
        await dialog_manager.done()
        return
    
    logging.info(f"Отправка задачи на сервер Django")

    dialog_manager.current_context().dialog_data["task_category"] = category_id

    # Используем текущее время и устанавливаем статус выполнения задачи в false
    import datetime
    current_time = datetime.datetime.now().isoformat()

    logging.info(f"Отправка задачи на сервер Django")
    
    # Получаем ID пользователя по его имени (или используем другой метод)
    user_id = await get_user_id_by_username(DJANGO_USERNAME)
    logging.info(f"Отправка задачи на сервер ")
    if not user_id:
        logging.info(f"Отправка задачи на сервер ")
        await message.answer("Не удалось получить ID пользователя.")
        return
    
    logging.info(f"Отправка задачи на сервер Django")

    token = await get_jwt_token()
    if not token:
        await message.answer("Не удалось получить токен для авторизации.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    task_title = dialog_manager.current_context().dialog_data["task_title"]
    task_description = dialog_manager.current_context().dialog_data.get("task_description", "")
    task_category = dialog_manager.current_context().dialog_data["task_category"]

    logging.info(f"Токен: {token}")

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{DJANGO_API_URL}tasks/", json={
            "title": task_title,
            "description": task_description,
            "due_date": current_time,
            "category": task_category,
            "user": user_id,  # Передаем ID пользователя
            "is_completed": False
        }, headers=headers) as response:
            status_code = response.status
            response_text = await response.text()

            logging.info(f"Отправка задачи на сервер Django: {status_code} - {response_text}")

            if status_code == 201:
                await dialog_manager.event.answer(
                    f"Задача добавлена: {dialog_manager.current_context().dialog_data['task_title']} "
                    f"(Категория: {input_value})"
                )
            else:
                await dialog_manager.event.answer("Произошла ошибка при добавлении задачи.")
    
    await dialog_manager.done()




# Диалоги для добавления задачи
task_dialog = Dialog(
    Window(
        Const("Введите название задачи:"),
        TextInput(id="task_title", on_success=process_task_title),
        state=TaskDialog.waiting_for_task_title
    ),
    Window(
        Const("Введите описание задачи:"),
        TextInput(id="task_description", on_success=process_task_description),
        state=TaskDialog.waiting_for_task_description
    ),
    Window(
        Const("Введите категорию задачи:"),
        TextInput(id="task_category", on_success=process_task_category),
        state=TaskDialog.waiting_for_task_category
    ),
)

# Регистрация диалога
registry.register(task_dialog)

# Добавление комментария к задаче через диалог
@dp.message_handler(commands=['add_comment'])
async def add_comment_handler(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(CommentDialog.waiting_for_task_id)

# Обработка завершения ввода ID задачи
async def process_comment_task_id(dialog_manager: DialogManager, text: str):
    dialog_manager.current_context().dialog_data["task_id"] = text
    await dialog_manager.dialog().next(dialog_manager)

# Обработка завершения ввода комментария
async def process_comment(dialog_manager: DialogManager, text: str):
    data = dialog_manager.current_context().dialog_data
    task_id = data["task_id"]
    add_comment(task_id, text, dialog_manager.event.from_user.id)
    await dialog_manager.event.answer(f"Комментарий добавлен к задаче {task_id}")
    await dialog_manager.done()

# Диалоги для добавления комментария
comment_dialog = Dialog(
    Window(
        Const("Введите ID задачи:"),
        TextInput(id="task_id", on_success=process_comment_task_id),  # Обработчик завершения ввода
        state=CommentDialog.waiting_for_task_id
    ),
    Window(
        Const("Введите комментарий:"),
        TextInput(id="comment_text", on_success=process_comment),  # Обработчик завершения ввода
        state=CommentDialog.waiting_for_comment
    ),
)

# Регистрация диалога для комментариев
registry.register(comment_dialog)

# Получение комментариев к задаче
@dp.message_handler(commands=['comments'])
async def list_comments(message: types.Message):
    task_id = message.get_args()
    comments = await get_comments(task_id)
    if comments:
        comment_list = "\n".join([f"Комментарий: {c['comment']}" for c in comments])
        await message.answer(f"Комментарии к задаче {task_id}:\n{comment_list}")
    else:
        await message.answer("Нет комментариев к этой задаче.")



# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)