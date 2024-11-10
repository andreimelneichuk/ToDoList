import logging
from aiogram import types
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import DialogRegistry
from config import API_TOKEN
from dialogs import register_dialogs
from tasks import register_task_handlers
from comments import register_comment_handlers
from login import register_login_handlers
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Базовые настройки бота
logging.basicConfig(level=logging.INFO)

# Создаем клавиатуру
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/view_tasks"))
    keyboard.add(KeyboardButton("/add_task"))
    keyboard.add(KeyboardButton("/add_comment"))
    keyboard.add(KeyboardButton("/view_comments"))
    keyboard.add(KeyboardButton("/register"))
    keyboard.add(KeyboardButton("/login"))
    return keyboard

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
registry = DialogRegistry(dp)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Привет! Я ваш ToDo List бот. Выберите команду:", reply_markup=create_main_keyboard())

# Регистрация диалогов
register_dialogs(dp, registry)
register_login_handlers(dp, registry)
register_task_handlers(dp, registry)
register_comment_handlers(dp, registry)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)