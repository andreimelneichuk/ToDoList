import logging
import aiohttp
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import TextInput
from config import DJANGO_API_URL, set_django_tokens, set_django_credentials

class LoginDialog(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

async def process_username(message: types.Message, widget, dialog_manager: DialogManager, input_value: str):
    dialog_manager.current_context().dialog_data["username"] = input_value
    await dialog_manager.switch_to(LoginDialog.waiting_for_password)

async def process_password(message: types.Message, widget, dialog_manager: DialogManager, input_value: str):
    dialog_manager.current_context().dialog_data["password"] = input_value
    await handle_login(dialog_manager)

async def handle_login(dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    username = data["username"]
    password = data["password"]

    logging.info(f"Пользователь пытается войти: {username}")

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{DJANGO_API_URL}token/", json={"username": username, "password": password}) as response:
            if response.status == 200:
                tokens = await response.json()
                set_django_tokens(tokens['access'], tokens['refresh'])
                set_django_credentials(username, password)
                await dialog_manager.event.answer("Успешный вход!")
            else:
                error_message = "Ошибка входа. Проверьте имя пользователя и пароль."
                await dialog_manager.event.answer(error_message)

    await dialog_manager.done()  # Завершение диалога

login_dialog = Dialog(
    Window(
        Const("Введите ваше имя пользователя:"),
        TextInput(id='username', on_success=process_username),
        state=LoginDialog.waiting_for_username,
    ),
    Window(
        Const("Введите ваш пароль:"),
        TextInput(id='password', on_success=process_password),
        state=LoginDialog.waiting_for_password,
    ),
)

# Переместите эту функцию на верхний уровень
async def start_login_dialog(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(LoginDialog.waiting_for_username)

def register_login_handlers(dp, registry):
    registry.register(login_dialog)
    dp.message_handler(commands=["login"])(start_login_dialog)