import datetime
import logging

from pathlib import Path
from typing import Callable, Iterable, NoReturn

import aiogram
from aiogram import filters, types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

from . import config, persistence

bot = aiogram.Bot(token=config.get_token())
dispatcher = aiogram.Dispatcher(bot)


def bot_admin_filter(message: types.Message) -> bool:
    return bool(
        persistence.BotAdmin.select().where(
            persistence.BotAdmin.user_id == message.from_user.id
        )
    )


_commands: list[types.BotCommand] = []


def command(
    name: str,
    *aliases: str,
    filters: Iterable[Callable[[types.Message], bool]] = [],
    description: str | None = None,
    **kwargs,
):
    if description:  # todo: i18n & l10n
        _commands.append(types.BotCommand(name, description))
    return dispatcher.message_handler(*filters, commands=[name, *aliases], **kwargs)


async def register_commands():
    return await bot.set_my_commands(_commands)


async def message_admins(text: str):
    for admin in persistence.BotAdmin.select():
        try:
            await bot.send_message(chat_id=admin.user_id, text=text)
        except Exception as e:
            logging.error(f"Error sending {text!r} to admin {admin.user_id}: {e}")


def add_basic_commands():
    @command("source", "opensource", "github")
    async def github_link(message: types.Message):
        return await message.reply(
            "https://github.com/SandaruKasa/SKTG/tree/python",
            disable_web_page_preview=True,
        )

    @command("shrug")
    async def shrug(message: types.Message):
        return await message.reply(r"¯\_(ツ)_/¯")

    @command("uptime", filters=(bot_admin_filter,))
    async def uptime(message: types.Message):
        result = config.get_uptime()
        if result is None:
            result = "Unknown"
        else:
            # stripping microseconds
            result = str(result).split(".")[0]
        return await message.reply(text=result)


i18n: I18nMiddleware | None = None


def gettext(message) -> str:
    return i18n(message)


def ngettext(msgid1: str, msgid2: str, n: int) -> str:
    return i18n(msgid1, msgid2, n)


def setup_i18n(
    i18n_domain="bot", locales_dir: Path = Path("locales")
) -> I18nMiddleware:
    global i18n
    i18n = I18nMiddleware(i18n_domain, locales_dir)
    dispatcher.middleware.setup(i18n)
    return i18n


def start_polling() -> NoReturn:
    async def on_startup(dp: aiogram.dispatcher):
        add_basic_commands()
        await register_commands()
        await message_admins("Hello!")
        config.startup_time = datetime.datetime.now()

    async def on_shutdown(dp: aiogram.dispatcher):
        logging.info("Stopping...")
        await message_admins("Goodbye!")

    aiogram.executor.start_polling(
        dispatcher=dispatcher,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
