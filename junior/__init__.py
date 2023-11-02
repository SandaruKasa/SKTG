import asyncio
import logging
import os
from pathlib import Path

from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from . import features, persistence, scheduler, telegram

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=r"%Y-%m-%dT%H-%M-%S",
)


async def start_polling(
    dispatcher: Dispatcher,
    bot: telegram.Bot,
):
    await bot.set_my_commands(telegram._commands)
    await telegram.message_admins(bot, "Hello!")
    try:
        await dispatcher.start_polling(bot)
    finally:
        await telegram.message_admins(bot, "Goodbye!")


def create_dispatcher():
    dispatcher = Dispatcher()

    # TODO: read env for locale path
    i18n = I18n(domain="bot", path=Path(__file__).parent / "locales")
    i18n_middleware = SimpleI18nMiddleware(i18n)
    dispatcher.message.middleware(i18n_middleware)
    dispatcher.callback_query.middleware(i18n_middleware)
    dispatcher.include_routers(*features.ROUTERS)

    return dispatcher


def main():
    logging.info("Starting...")
    persistence.init()
    scheduler.start()
    asyncio.run(
        start_polling(
            dispatcher=create_dispatcher(),
            bot=telegram.Bot(token=config.get_token()),
        )
    )
