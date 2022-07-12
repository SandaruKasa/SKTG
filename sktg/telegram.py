from typing import Callable, Iterable

import aiogram
from aiogram import types, filters

from . import config, persistence

bot = aiogram.Bot(token=config.token)
dp = aiogram.Dispatcher(bot)


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
    admin_only: bool = False,
    **kwargs
):
    if description:  # todo: i18n & l10n
        _commands.append(types.BotCommand(name, description))

    filters = list(filters)
    if admin_only:
        filters.append(bot_admin_filter)
    return dp.message_handler(*filters, commands=[name, *aliases], **kwargs)


async def register_commands():
    return await bot.set_my_commands(_commands)
