from aiogram import Router
from aiogram.types.message import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import get_user_by_telegram_id, add_queue
from utils import validation_on_admin
from config import SECRET_ADMIN_KEY


router = Router()


@router.message(Command("new_queue"))
async def new_queue_command(message: Message):
    telegram_id = message.from_user.id

    if await get_user_by_telegram_id(telegram_id=telegram_id) and await validation_on_admin(telegram_id):
        # получаем текст сообщения
        message_text = message.text

        if len(message_text.split()) > 1: # если есть какой-то текст помимо команды, создаем очередь
            title = message_text.split(maxsplit=1)[1]

            # Отправляем сообщение с очередью
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="join_to_queue"))
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="quit_from_queue"))
            builder.adjust(1)
            sent_message = await message.answer(f"<b>{title}</b>", reply_markup=builder.as_markup())
            # Получаем все необходимы данные из отправленного сообщения
            message_id = sent_message.message_id
            chat_id = sent_message.chat.id

            print("Создана очередь", title, message_id, chat_id)
            # Добавляем очередь в таблицу
            await add_queue(title, chat_id, message_id)

        else: # если текста нет, возвращаем сообщение об ошибки
            await message.reply("Добавье название очереди.\nПример:\n/new_queue Очередь на лабораторную")
    else:
        await message.answer("Эту команду могут использовать только админы")
