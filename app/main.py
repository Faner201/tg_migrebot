import argparse
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from app import bot as bot_pkg
from app.config import settings

logger = logging.getLogger(__name__)


async def run_bot() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=None),
    )
    dp = Dispatcher()
    bot_pkg.register_handlers(dp)
    logger.info("Starting polling")
    await dp.start_polling(bot)


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrebot MVP")
    parser.add_argument("--check", action="store_true", help="Run dependency/config check")
    args = parser.parse_args()

    setup_logging()

    if args.check:
        logger.info("Check succeeded")
        return

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()

