import logging, aiohttp
from aiogram import Dispatcher, types
from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import TextInput
from aiogram.dispatcher.filters.state import State, StatesGroup
from api import get_tasks, get_category_by_name, get_jwt_token, get_user_id_by_username
from config import DJANGO_USERNAME, DJANGO_API_URL

class TaskDialog(StatesGroup):
    waiting_for_task_title = State()
    waiting_for_task_description = State()
    waiting_for_task_category = State()

async def process_task_title(message, widget, dialog_manager, input_value):
    dialog_manager.current_context().dialog_data["task_title"] = input_value
    await dialog_manager.switch_to(TaskDialog.waiting_for_task_description)

async def process_task_description(message, widget, dialog_manager, input_value):
    dialog_manager.current_context().dialog_data["task_description"] = input_value
    await dialog_manager.switch_to(TaskDialog.waiting_for_task_category)

async def process_task_category(message: types.Message, widget, dialog_manager: DialogManager, input_value: str):
    logging.info(f"Добавление задачи на сервер Django:")

    # Проверяем существование категории
    category_id = await get_category_by_name(input_value, dialog_manager)
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
    user_id = await get_user_id_by_username(DJANGO_USERNAME,dialog_manager)
    logging.info(f"Отправка задачи на сервер ")
    if not user_id:
        logging.info(f"Отправка задачи на сервер ")
        await message.answer("Не удалось получить ID пользователя.")
        return
    
    logging.info(f"Отправка задачи на сервер Django")

    token = await get_jwt_token(dialog_manager)
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

task_dialog = Dialog(
    Window(Const("Введите название задачи:"), TextInput(id="task_title", on_success=process_task_title), state=TaskDialog.waiting_for_task_title),
    Window(Const("Введите описание задачи:"), TextInput(id="task_description", on_success=process_task_description), state=TaskDialog.waiting_for_task_description),
    Window(Const("Введите категорию задачи (make, list или remind):"), TextInput(id="task_category", on_success=process_task_category), state=TaskDialog.waiting_for_task_category),
)

def register_task_handlers(dp: Dispatcher, registry):
    registry.register(task_dialog)

    @dp.message_handler(commands=['view_tasks'])
    async def view_tasks_handler(message: types.Message):
        user_id = message.from_user.id  # Или используйте метод получения user_id
        tasks = await get_tasks(user_id)  # Получаем задачи для пользователя

        if tasks:
            task_list = "\n".join([f"ID: {task['id']}, Задача: {task['title']}, Дата: {task['due_date']}" for task in tasks])
            await message.answer(f"Ваши задачи:\n{task_list}")
        else:
            await message.answer("У вас нет задач.")
    
    @dp.message_handler(commands=['add_task'])
    async def add_task(message: types.Message, dialog_manager: DialogManager):
        await dialog_manager.start(TaskDialog.waiting_for_task_title, mode=StartMode.RESET_STACK)