import logging

from aiogram import Bot, F, Router, exceptions, filters, types
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.i18n import gettext, ngettext

from . import persistence


def filter_admins(message: types.Message) -> bool:
    return bool(
        persistence.BotAdmin.select().where(
            persistence.BotAdmin.user_id == message.from_user.id
        )
    )


async def message_admins(bot: Bot, text: str):
    for admin in persistence.BotAdmin.select():
        try:
            await bot.send_message(chat_id=admin.user_id, text=text)
        except Exception as e:
            logging.error(f"Error sending {text!r} to admin {admin.user_id}: {e}")


_commands: list[types.BotCommand] = []


# TODO: i18n
def create_command(names: list[str], description: str):
    _commands.append(types.BotCommand(command=names[0], description=description))
    return filters.Command(*names)
