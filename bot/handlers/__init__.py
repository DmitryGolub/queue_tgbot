from aiogram import Dispatcher
from .admin import router as admin_router
from .delete_queue import router as delete_queue_router
from .new_queue import router as new_queue_router
from .register import router as register_router
from .start import router as start_router


def register_all_handlers(dp: Dispatcher) -> None:
    dp.include_routers(
        admin_router,
        delete_queue_router,
        new_queue_router,
        register_router,
        start_router,
    )
