import asyncio
from time import sleep

from aiogram import Dispatcher, Bot
from aiogram.types.message import Message
from aiogram.filters import Command

from lab_queue import QueueLab
from config import BOT_TOKEN


dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)

lab_queue = None


@dp.message(Command("start"))
async def command_start(message: Message) -> None:
    await message.answer(f"Hello {message.from_user.username}")


@dp.message(Command("new_queue"))
async def command_start(message: Message) -> None:
    message_text = message.text

    if len(message_text.split()) > 1:
        title_queue = message_text.split(maxsplit=1)[1]
        lab_queue = QueueLab(title_queue)
        print(lab_queue)
    else:
        await message.reply("Укажите заголовок. Пример: /new_queue Название очерди")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
