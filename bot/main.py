import asyncio

from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import register_all_handlers
from callbacks import register_all_callbacks
from core import bot


dp = Dispatcher()


async def main() -> None:
    register_all_callbacks(dp)
    register_all_handlers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
