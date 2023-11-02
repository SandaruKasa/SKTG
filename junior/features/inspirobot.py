import datetime

import aiohttp

from ..telegram import *

ROUTER = aiogram.Router(name="inspirobot")


# TODO: allow user to choose xmas / inspirobot
@ROUTER.message(
    create_command(
        names=["inspire", "inspirobot"],
        description="AI-generated inspirational quote",
    )
)
async def inspire(message: types.Message):
    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        today = datetime.date.today()
        if (
            today.month == 12
            and today.day >= 20
            or today.month == 1
            and today.day <= 14
        ):
            site = "xmascardbot.com"
        else:
            site = "inspirobot.me"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://{site}/api", params={"generate": "true"}
            ) as response:
                picture_url = await response.text()

        return await message.reply_photo(
            photo=picture_url,
            caption=f"https://{site}/share?iuid={picture_url.split(site)[-1].strip('/')}",
        )
