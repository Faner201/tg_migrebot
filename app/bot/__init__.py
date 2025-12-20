from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.bot.router import setup_router


def register_handlers(dp: Dispatcher) -> None:
    setup_router(dp)


async def setup_commands_menu(bot: Bot) -> None:
    """Установить меню команд бота."""
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Справка по командам"),
        BotCommand(command="headache", description="Быстрый старт записи"),
        BotCommand(command="entry", description="Создать запись на сегодня"),
        BotCommand(command="today", description="Показать запись за сегодня"),
        BotCommand(command="edit", description="Редактировать запись"),
        BotCommand(command="recent", description="Последние записи"),
        BotCommand(command="export", description="Выгрузить записи (CSV/XLSX)"),
        BotCommand(command="migrebotplus", description="Статус подписки"),
    ]
    await bot.set_my_commands(commands)



