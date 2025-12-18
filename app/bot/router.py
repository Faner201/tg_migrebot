from aiogram import Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "👋 Я Migrebot (MVP). Пока готовлю инфраструктуру. "
        "Команды будут добавлены позже."
    )


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong")


def setup_router(dp: Dispatcher) -> None:
    dp.include_router(router)

