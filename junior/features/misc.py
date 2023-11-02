from datetime import datetime

from ..telegram import *

ROUTER = Router(name="misc")


@ROUTER.message(filters.Command("source", "opensource", "github"))
async def github_link(message: types.Message):
    return await message.reply(
        "https://github.com/SandaruKasa/SKTG/tree/python",
        disable_web_page_preview=True,
    )


@ROUTER.message(filters.Command("shrug"))
async def shrug(message: types.Message):
    return await message.reply(r"¯\_(ツ)_/¯")


startup_time: datetime = datetime.now()


@ROUTER.message(filters.Command("uptime"), filter_admins)
async def uptime(message: types.Message):
    return await message.reply(
        text="Unknown"
        if startup_time is None
        # stripping microseconds
        else str(datetime.now() - startup_time).split(".")[0]
    )
