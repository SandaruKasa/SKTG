from ..telegram import *


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
    result = get_uptime()
    if result is None:
        result = "Unknown"
    else:
        # stripping microseconds
        result = str(result).split(".")[0]
    return await message.reply(text=result)
