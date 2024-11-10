import logging
from aiogram import Dispatcher
from api import get_comments, add_comment
from aiogram import Dispatcher, types
from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import TextInput
from aiogram.dispatcher.filters.state import State, StatesGroup


class CommentDialog(StatesGroup):
    waiting_for_task_id = State()
    waiting_for_comment = State()

# Обработка завершения ввода ID задачи
async def process_comment_task_id(message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.current_context().dialog_data["task_id"] = text  # Используйте dialog_manager.data для сохранения данных
    await dialog_manager.dialog().next(dialog_manager)

async def process_comment(message, widget, dialog_manager: DialogManager, text: str):
    task_id = dialog_manager.current_context().dialog_data["task_id"]  # Достаем данные задачи из dialog_manager.data
    await add_comment(task_id, text, dialog_manager.event.from_user.id)
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
 

def register_comment_handlers(dp: Dispatcher, registry):
    registry.register(comment_dialog)

    @dp.message_handler(commands=['add_comment'])
    async def add_comment_handler(message: types.Message, dialog_manager: DialogManager):
        await dialog_manager.start(CommentDialog.waiting_for_task_id)

    # Получение комментариев к задаче
    @dp.message_handler(commands=['view_comments'])
    async def view_comments_handler(message: types.Message):
        task_id = message.get_args()
        comments = await get_comments(task_id)
        if comments:
            comment_list = "\n".join([f"Комментарий: {c['comment']}" for c in comments])
            await message.answer(f"Комментарии к задаче {task_id}:\n{comment_list}")
        else:
            await message.answer("Нет комментариев к этой задаче.")