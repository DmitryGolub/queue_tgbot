from aiogram import Dispatcher

from .join_to_queue import router as join_to_queue_router
from .quit_from_queue import router as quit_from_queue_router


def register_all_callbacks(dp: Dispatcher) -> None:
    dp.include_routers(
        join_to_queue_router,
        quit_from_queue_router,
    )
