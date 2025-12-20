"""Базовые команды бота."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.domain.models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    """Приветствие и краткое описание возможностей."""
    await message.answer(
        "Привет! Я Migrebot — помогаю вести дневник головной боли.\n"
        "Основные команды:\n"
        "/headache — быстрый старт записи\n"
        "/entry — создать запись на сегодня\n"
        "/today — показать запись за сегодня\n"
        "/recent — последние записи\n"
        "/help — подробности"
    )


@router.message(Command("help"))
async def cmd_help(message: Message, user: User) -> None:
    """Показать справку по командам."""
    await message.answer(
        "Доступные команды:\n"
        "/headache — краткая сводка по записи на сегодня\n"
        "/entry — создать запись на сегодня\n"
        "/today — показать запись за сегодня\n"
        "/edit — подсказки по редактированию записи\n"
        "/set_score <1-10> — оценка боли\n"
        "/set_pain_desc <текст> — описание боли\n"
        "/set_pain <уровень> — установить боль (none|mild|moderate|severe|very_severe)\n"
        "/set_notes <текст> — добавить заметки\n"
        "/set_attack — отметить приступ\n"
        "/add_med <тип> <название> [дозировка] — добавить препарат\n"
        "/recent — показать последние записи\n"
        "/export [csv|xlsx] — выгрузка записей за 30 дней\n"
        "/migrebotplus — статус подписки (MVP)"
    )


@router.message(Command("migrebotplus"))
async def cmd_migrebot_plus(message: Message, user: User) -> None:
    """Заглушка статуса Migrebot+ (MVP)."""
    await message.answer(
        "Migrebot+ скоро появится. Пока доступен базовый дневник и статистика.\n"
        "Оставьте обратную связь, какие функции вам нужны в подписке."
    )



