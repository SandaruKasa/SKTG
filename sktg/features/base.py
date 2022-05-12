"""Basic functionality I would like all the bots to have.
"""

from .. import config
from ..telegram import *


@dp.message_handler(commands=["source", "opensource", "github"])
async def github_link(message: types.Message):
    return await message.reply(
        "https://github.com/SandaruKasa/SKTG/tree/async",
        disable_web_page_preview=True,
    )


@dp.message_handler(commands=["shrug"])
async def shrug(message: types.Message):
    return await message.reply(r"¯\_(ツ)_/¯")


@dp.message_handler(bot_admin_filter, commands=["uptime"])
async def uptime(message: types.Message):
    result = config.get_uptime()
    if result is None:
        result = "Unknown"
    else:
        # stripping microseconds
        result = str(result).split(".")[0]
    return await message.reply(text=result)
