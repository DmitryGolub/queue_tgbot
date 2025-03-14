from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import get_user_by_telegram_id, get_user_in_queue, delete_user_from_queue, get_users_in_queue, get_queue_by_chat_message_id
from core import bot


router = Router()


@router.callback_query(F.data == "quit_from_queue")
async def quit_to_queue_callback(callback: CallbackQuery) -> None:
    telegram_id = callback.from_user.id
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    if await get_user_by_telegram_id(telegram_id=telegram_id): # Проверяем, что пользователь авторизован

        if await get_user_in_queue(telegram_id=telegram_id, message_id=message_id, chat_id=chat_id):

            await delete_user_from_queue(telegram_id=telegram_id, chat_id=chat_id, message_id=message_id)

            users_in_queue = await get_users_in_queue(message_id=message_id, chat_id=chat_id)
            queue = await get_queue_by_chat_message_id(message_id=message_id, chat_id=chat_id)
            
            # Обновляем сообщение с очередью
            new_text = f"<b>{queue['title']}\n</b>"

            for index, user in enumerate(users_in_queue):
                new_text += f"{index + 1}. {user['name']}\n"
            
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="join_to_queue"))
            builder.add(InlineKeyboardButton(text="Выйти из очереди", callback_data="quit_from_queue"))
            builder.adjust(1)

            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, reply_markup=builder.as_markup())

            await callback.answer("Вы вышли из очереди")
        
        else:
            await callback.answer("Вас нет в очереди")
    else:
        await callback.answer("Вы не зарегистрированы") 
