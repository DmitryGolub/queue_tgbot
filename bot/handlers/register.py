from aiogram import Router
from aiogram.types.message import Message
from aiogram.filters import Command

from database.database import get_user_by_telegram_id, add_user
from config import SECRET_ADMIN_KEY


router = Router()


@router.message(Command("register"))
async def register_user_command(message: Message) -> None:
    # получаем telegram_id
    telegram_id = message.from_user.id

    # получаем текст сообщения
    message_text = message.text

    if len(message_text.split()) > 1: # если есть какой-то текст помимо команды
        name = message_text.split(maxsplit=1)[1]
        
        # проверяем, есть ли такой пользователь в users
        if await get_user_by_telegram_id(telegram_id=telegram_id): # если есть, выводим сообщение
            await message.answer("Вы уже зарегистрировались")

        else: # если нет, добавляем
            await add_user(telegram_id, name)
            await message.answer("Вы успешно авторизовались")

    else: # если текста нет, возвращаем сообщение об ошибки
        await message.reply("Укажите Имя и Фамилию.\nПример:\n/register Иван Иванов")
    