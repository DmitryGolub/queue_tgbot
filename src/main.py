import asyncio

from aiogram import Dispatcher, Bot, F
from aiogram.types.message import Message
from aiogram.types import CallbackQuery
from aiogram.filters import Command

from database import add_user, get_user_by_telegram_id
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


@dp.message(Command("register"))
async def register_user_command(message: Message):
    # получаем telegram_id
    telegram_id = message.from_user.id

    # получаем текст сообщения
    message_text = message.text

    if len(message_text.split()) > 1: # если есть какой-то текст помимо команды
        name = message_text.split(maxsplit=1)[1]
        
        # проверяем, есть ли такой пользователь в users
        if get_user_by_telegram_id(telegram_id=telegram_id): # если есть, выводим сообщение
            await message.answer("Вы уже зарегистрировались")

        else: # если нет, добавляем
            add_user(telegram_id, name)
            await message.answer("Вы успешно авторизовались")

    else: # если текста нет, возвращаем сообщение об ошибки
        await message.reply("Укажите Имя и Фамилию. Пример: /register Иван Иванов")
    

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
