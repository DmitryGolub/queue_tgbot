import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types.message import Message
from aiogram.filters import Command

from database import add_user, get_notices, add_notice, delete_notices
from schemas import QueueLab
from config import BOT_TOKEN


dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)

lab_queue = None


@dp.message(Command("start"))
async def command_start(message: Message) -> None:
    await message.answer(f"Hello {message.from_user.username}")
    

@dp.message(Command("register"))
async def command_register(message: Message) -> None:
    telegram_id = int(message.from_user.id)
    message_text = message.text

    if len(message_text.split()) > 1:
        name = message_text.split(maxsplit=1)[1]
        response = add_user(telegram_id, name)
        await message.answer(response)
    else:
        await message.reply("Укажите Имя и Фамилию. Пример: /register Иван Иванов")


@dp.message(Command("new_queue"))
async def command_new_queue(message: Message) -> None:
    global lab_queue
    message_text = message.text

    if len(message_text.split()) > 1:
        title_queue = message_text.split(maxsplit=1)[1]
        lab_queue = QueueLab(title_queue)
    else:
        await message.reply("Укажите заголовок. Пример: /new_queue Название очереди")


@dp.message(Command("join"))
async def command_join_to_queue(message: Message) -> None:
    if lab_queue:
        telegram_id = message.from_user.id
        response = lab_queue.add_user(telegram_id)
        if response:

            message_queue = await message.answer(str(lab_queue))
            
            message_id = message_queue.message_id
            response = add_notice(telegram_id, message_id)
            await message.answer(response)
        else:
            await message.answer("Вы уже в очереди")


@dp.message(Command("drop_queue"))
async def command_drop_queue(message: Message) -> None:
    global lab_queue
    if lab_queue:
        lab_queue = None
        delete_notices()
    else:
        await message.answer("Нет очереди")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
