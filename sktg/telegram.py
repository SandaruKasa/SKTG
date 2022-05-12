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
