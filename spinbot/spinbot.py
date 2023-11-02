import asyncio
import logging
import os
import re

import aiogram

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=r"%Y-%m-%dT%H-%M-%S",
)


def get_token() -> str:
    token = os.getenv("BOT_TOKEN")
    if token is None:
        with open(os.getenv("BOT_TOKEN_FILE", "token.txt")) as f:
            token = f.read().strip()
    return token


bot = aiogram.Bot(token=get_token())
dispatcher = aiogram.Dispatcher()


PICTURE = "https://i.redd.it/09su7inm63z31.jpg"


@dispatcher.message(
    aiogram.F.text.regexp(
        pattern=r"(?<!\w)спин(?!\w)",
        flags=re.UNICODE | re.IGNORECASE,
    )
)
async def spin(message: aiogram.types.Message):
    global PICTURE
    result = await message.reply_photo(photo=PICTURE)
    # Use file_id instead of URL after the first upload.
    # Not really necessary, but still a good thing to do.
    if PICTURE.startswith("http"):
        PICTURE = max(result.photo, key=lambda ps: ps.width * ps.height).file_id


if __name__ == "__main__":
    asyncio.run(dispatcher.start_polling(bot))
