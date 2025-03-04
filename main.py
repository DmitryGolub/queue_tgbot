import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types.message import Message
from aiogram.filters import Command


from config import BOT_TOKEN


dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)


@dp.message(Command("start"))
async def command_start(message: Message) -> None:
    await message.answer(f"Hello {message.from_user.username}")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
