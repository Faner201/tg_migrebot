"""Middleware для бота."""

import logging
from time import perf_counter
from typing import Any, Awaitable, Callable
from uuid import uuid4

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, User as TelegramUser

from app.adapters import get_session
from app.adapters.repository import UserRepository

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Простая трассировка апдейтов."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        trace_id = uuid4().hex
        data["trace_id"] = trace_id
        started = perf_counter()
        try:
            return await handler(event, data)
        finally:
            elapsed_ms = (perf_counter() - started) * 1000
            update: Update | None = data.get("event_update")
            update_type = "unknown"
            user_id = None

            # aiogram >=3 передает event как Message/CallbackQuery; event_update может быть None
            source = update or event
            if hasattr(source, "message"):
                update_type = "message"
                from_user = source.message.from_user  # type: ignore[attr-defined]
                user_id = from_user.id if from_user else None
            elif hasattr(source, "callback_query"):
                update_type = "callback"
                from_user = source.callback_query.from_user  # type: ignore[attr-defined]
                user_id = from_user.id if from_user else None
            elif hasattr(source, "from_user"):
                # когда event уже Message/CallbackQuery
                update_type = source.__class__.__name__.lower()
                from_user = source.from_user  # type: ignore[attr-defined]
                user_id = from_user.id if from_user else None

            logger.info(
                "trace_id=%s update_type=%s user_id=%s elapsed_ms=%.1f",
                trace_id,
                update_type,
                user_id,
                elapsed_ms,
            )


class UserMiddleware(BaseMiddleware):
    """Middleware для получения/создания пользователя."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Обработать обновление и добавить пользователя в data."""
        update: Update | None = data.get("event_update")

        telegram_user: TelegramUser | None = None
        if update and update.message:
            telegram_user = update.message.from_user
        elif update and update.callback_query:
            telegram_user = update.callback_query.from_user
        elif hasattr(event, "from_user"):
            telegram_user = event.from_user  # type: ignore[attr-defined]

        if telegram_user is None:
            return await handler(event, data)

        async for session in get_session():
            repo = UserRepository(session)
            user = await repo.get_or_create(
                telegram_id=telegram_user.id, username=telegram_user.username
            )
            data["user"] = user
            await session.commit()
            break

        return await handler(event, data)
