import datetime
import logging
from typing import Callable, Iterable, NoReturn

import aiogram
from aiogram import filters, types

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


startup_time: None | datetime.datetime = None


def get_uptime() -> datetime.timedelta | None:
    if startup_time is not None:
        return datetime.datetime.now() - startup_time
    else:
        return None


def start_polling() -> NoReturn:
    async def on_startup(dp: aiogram.dispatcher):
        await register_commands()
        await message_admins("Hello!")
        global startup_time
        startup_time = datetime.datetime.now()

    async def on_shutdown(dp: aiogram.dispatcher):
        logging.info("Stopping...")
        await message_admins("Goodbye!")

    aiogram.executor.start_polling(
        dispatcher=dispatcher,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
