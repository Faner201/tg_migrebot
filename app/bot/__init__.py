from aiogram import Dispatcher

from app.bot.router import setup_router


def register_handlers(dp: Dispatcher) -> None:
    setup_router(dp)

