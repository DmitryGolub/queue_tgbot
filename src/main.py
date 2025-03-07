import asyncio

from aiogram import Dispatcher, Bot, F
from aiogram.types.message import Message
from aiogram.types import CallbackQuery
from aiogram.filters import Command

from config import BOT_TOKEN


dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("""
                         Что я умею
                         /register - регистрация пользователя
                         /admin - стать админом
                         Команды для админа
                         /new_queue - создать новую очередь
                         /drop_queue - удалить очередь""")


@dp.message(Command("set_admin"))
async def set_admin_command(message: Message):
    ...


@dp.message(Command("new_queue"))
async def new_queue_command(message: Message):
    ...


@dp.message(Command("drop_queue"))
async def drop_queue_command(message: Message):
    ...


@dp.callback_query(F.data == "join_to_queue")
async def join_to_queue_callback(callback: CallbackQuery):
    ...


@dp.callback_query(F.data == "quit_to_queue")
async def quit_to_queue_callback(callback: CallbackQuery):
    ...


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
