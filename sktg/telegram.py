from typing import Callable, Iterable

import aiogram
from aiogram import types

from . import config, persistance

bot = aiogram.Bot(token=config.token)
dp = aiogram.Dispatcher(bot)


def bot_admin_filter(message: types.Message) -> bool:
    return bool(
        persistance.BotAdmin.select().where(
            persistance.BotAdmin.user_id == message.from_user.id
        )
    )


_commands: list[types.BotCommand] = []


def command(
    name: str,
    *aliases: str,
    filters: Iterable[Callable[[types.Message], bool]] = [],
    description: str | None = None,
    admin_only: bool = False,
):
    if description:  # todo: i18n & l10n
        _commands.append(types.BotCommand(name, description))

    filters = list(filters)
    if admin_only:
        filters.append(bot_admin_filter)
    return dp.message_handler(*filters, commands=[name, *aliases])


async def register_commands():
    return await bot.set_my_commands(_commands)


def extract_links(message: types.Message):
    for entity in message.entities:
        if entity.type == types.MessageEntityType.TEXT_LINK:
            yield entity.url
        elif entity.type == types.MessageEntityType.URL:
            yield entity.get_text(message.text or message.caption)
