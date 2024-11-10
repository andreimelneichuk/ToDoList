from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.text import Const
from aiogram import types, Dispatcher
from aiogram_dialog.widgets.input import TextInput
from aiogram.dispatcher.filters.state import State, StatesGroup
from api import register_user
from config import DJANGO_API_URL, set_django_credentials, set_django_tokens
import logging, aiohttp

class RegistrationDialog(StatesGroup):
    start = State()
    ask_password = State()
    ask_email = State()

async def get_name(message, widget, dialog_manager, input_value):
    dialog_manager.current_context().dialog_data["username"] = input_value
    await dialog_manager.switch_to(RegistrationDialog.ask_password)

async def get_password(message, widget, dialog_manager, input_value):
    dialog_manager.current_context().dialog_data["password"] = input_value
    await dialog_manager.switch_to(RegistrationDialog.ask_email)

async def get_email(message, widget, dialog_manager, input_value):
    dialog_manager.current_context().dialog_data["email"] = input_value
    await register_user(dialog_manager)

# Функция регистрации
async def register_user(dialog_manager: DialogManager):
    from main import bot
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
                set_django_tokens(result.get('access'),result.get('refresh'))
                logging.info(f"Ответ от сервера: {result}")
                await bot.send_message(
                    dialog_manager.event.from_user.id, "Регистрация успешна!"
                )
                # Обновляем глобальные переменные через функцию
                set_django_credentials(username, password)
            else:
                error_message = result.get('detail', 'Неизвестная ошибка')
                await bot.send_message(
                    dialog_manager.event.from_user.id, f"Ошибка регистрации: {error_message}"
                )

    await dialog_manager.done()  # Завершение диалога

reg_dialog = Dialog(
    Window(Const("Введите ваше имя пользователя:"), TextInput(id='username', on_success=get_name), state=RegistrationDialog.start),
    Window(Const("Введите ваш пароль:"), TextInput(id='password', on_success=get_password), state=RegistrationDialog.ask_password),
    Window(Const("Введите ваш email:"), TextInput(id='email', on_success=get_email), state=RegistrationDialog.ask_email),
)

def register_dialogs(dp: Dispatcher, registry):
    registry.register(reg_dialog)
    # Стартовая команда для начала диалога
    @dp.message_handler(commands=["register"])
    async def start_dialog(message: types.Message, dialog_manager: DialogManager):
        logging.info("Команда /register получена")
        await dialog_manager.start(RegistrationDialog.start, mode=StartMode.RESET_STACK)