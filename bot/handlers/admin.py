from aiogram import Router
from aiogram.types.message import Message
from aiogram.filters import Command

from database.database import get_user_by_telegram_id, set_admin_user
from config import SECRET_ADMIN_KEY


router = Router()



@router.message(Command("admin"))
async def set_admin_command(message: Message):
    telegram_id = message.from_user.id

    if await get_user_by_telegram_id(telegram_id=telegram_id): # проверка на регистрацию

        # получаем текст сообщения
        message_text = message.text

        if len(message_text.split()) > 1: # если есть какой-то текст помимо команды
            text = message_text.split(maxsplit=1)[1]
            if text == SECRET_ADMIN_KEY:
                await set_admin_user(telegram_id=telegram_id)
                await message.answer("Теперь вы админ")
            else:
                await message.answer("Хорошая попытка")

        else:
            await message.answer("Нужно указать секретный ключ\nПример: \n/admin secret_key")

    else:
        await message.answer("Для начала нужно зарегистрироваться")
