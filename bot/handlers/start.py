from aiogram import Router
from aiogram.filters import Command
from aiogram.types.message import Message


router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Что я умею\n/register - регистрация пользователя\n/admin - стать админом\nКоманды для админа\n/new_queue - создать новую очередь\n/delete_queue - удалить очередь")
