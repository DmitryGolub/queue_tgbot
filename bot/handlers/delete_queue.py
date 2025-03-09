from aiogram import Router
from aiogram.types.message import Message
from aiogram.filters import Command

from database.database import get_user_by_telegram_id, get_queue_by_chat_message_id, delete_queues_by_chat_message_id
from utils import validation_on_admin
from core import bot


router = Router()


@router.message(Command("delete_queue"))
async def delete_queue_command(message: Message) -> None:
    telegram_id = message.from_user.id

    if await get_user_by_telegram_id(telegram_id=telegram_id) and await validation_on_admin(telegram_id): # Валидация на админа
        if message.reply_to_message: # Проверяем, что это был ответ на сообщение
            # Берем нужные данне из сообщения, на которое ответили
            reply_message_id = message.reply_to_message.message_id
            reply_chat_id = message.reply_to_message.chat.id

            # Проверка, что админ ответил на сообщение с очередью
            if await get_queue_by_chat_message_id(message_id=reply_message_id, chat_id=reply_chat_id):
                # Удаляем сообщение с очередью
                await bot.delete_message(chat_id=reply_chat_id, message_id=reply_message_id)
                # Удаляем запись из таблицы очередей
                await delete_queues_by_chat_message_id(chat_id=reply_chat_id, message_id=reply_message_id)

            else: # Ответил не на сообщение с очередью
                await message.answer("Нужно ответить на сообщение с очередью")
        else:
            await message.answer("Нужно ответить на сообщение с очередью")
    else:
        await message.answer("Эту команду могут использовать только админы")

