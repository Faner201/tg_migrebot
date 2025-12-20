from aiogram import Dispatcher, Router

from app.bot.handlers import common, entries
from app.bot.middleware import LoggingMiddleware, UserMiddleware

main_router = Router()
main_router.include_router(common.router)
main_router.include_router(entries.router)


def setup_router(dp: Dispatcher) -> None:
    """Настроить роутеры и middleware."""
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    dp.include_router(main_router)

