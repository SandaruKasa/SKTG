# TODO: separate this into feature-facing and __init__-facing APIs

import datetime
import logging
from pathlib import Path
from typing import Callable, Iterable, NoReturn

import aiogram
from aiogram import Router, filters, types
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware, gettext, ngettext

from . import config, persistence

bot = aiogram.Bot(token=config.get_token())
dispatcher = aiogram.Dispatcher()


def bot_admin_filter(message: types.Message) -> bool:
    return bool(
        persistence.BotAdmin.select().where(
            persistence.BotAdmin.user_id == message.from_user.id
        )
    )


_commands: list[types.BotCommand] = []


# TODO: i18n
def create_command(names: list[str], description: str):
    _commands.append(types.BotCommand(command=names[0], description=description))
    return aiogram.filters.Command(*names)


async def register_commands():
    return await bot.set_my_commands(_commands)


async def message_admins(text: str):
    for admin in persistence.BotAdmin.select():
        try:
            await bot.send_message(chat_id=admin.user_id, text=text)
        except Exception as e:
            logging.error(f"Error sending {text!r} to admin {admin.user_id}: {e}")


def setup_i18n(domain="bot", locales_dir: Path = Path("locales")) -> I18n:
    i18n = I18n(domain=domain, path=locales_dir)
    middleware = SimpleI18nMiddleware(i18n)
    dispatcher.message.middleware(middleware)
    dispatcher.callback_query.middleware(middleware)
    return i18n


@dispatcher.message(filters.Command("source", "opensource", "github"))
async def github_link(message: types.Message):
    return await message.reply(
        "https://github.com/SandaruKasa/SKTG/tree/python",
        disable_web_page_preview=True,
    )


@dispatcher.message(filters.Command("shrug"))
async def shrug(message: types.Message):
    return await message.reply(r"¯\_(ツ)_/¯")


startup_time: datetime.datetime | None = None


@dispatcher.message(filters.Command("uptime"), bot_admin_filter)
async def uptime(message: types.Message):
    return await message.reply(
        text="Unknown"
        if startup_time is None
        # stripping microseconds
        else str(datetime.datetime.now() - startup_time).split(".")[0]
    )


async def start_polling():
    global startup_time
    await register_commands()
    await message_admins("Hello!")
    startup_time = datetime.datetime.now()
    try:
        await dispatcher.start_polling(bot)
    finally:
        await message_admins("Goodbye!")
