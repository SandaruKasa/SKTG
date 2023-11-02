from datetime import datetime

from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from . import config, telegram
from .telegram import *

dispatcher = Dispatcher()


@dispatcher.message(filters.Command("source", "github"))
async def github_link(message: types.Message):
    return await message.reply(
        "https://github.com/SandaruKasa/SKTG/tree/python",
        disable_web_page_preview=True,
    )


@dispatcher.message(filters.Command("shrug"))
async def shrug(message: types.Message):
    return await message.reply(r"¯\_(ツ)_/¯")


startup_time: datetime | None = None


@dispatcher.message(filters.Command("uptime"), filter_admins)
async def uptime(message: types.Message):
    return await message.reply(
        text="Unknown"
        if startup_time is None
        # stripping microseconds
        else str(datetime.now() - startup_time).split(".")[0]
    )


def init_i18n(domain):
    i18n = I18n(domain=domain, path=config.get_locale_path())
    i18n_middleware = SimpleI18nMiddleware(i18n)
    dispatcher.message.middleware(i18n_middleware)
    dispatcher.callback_query.middleware(i18n_middleware)


async def start_polling(bot: Bot):
    global startup_time
    startup_time = datetime.now()
    await bot.set_my_commands(telegram._commands)
    await message_admins(bot, "Hello!")
    try:
        await dispatcher.start_polling(bot)
    finally:
        await message_admins(bot, "Goodbye!")
