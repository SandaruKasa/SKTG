import re
from typing import Generator

from ..telegram import *


def extract_links(message: types.Message) -> Generator[str, None, None]:
    for entity in message.entities:
        if entity.type == types.MessageEntityType.TEXT_LINK:
            yield entity.url
        elif entity.type == types.MessageEntityType.URL:
            yield entity.get_text(message.text or message.caption)


# [\w] gives [0-9a-zA-Z_] in ASCII mode
# `.*` in the beginning to prevent www.youtu.be from hapenning
# `.*` in the end to get rid of ?feature=share and other useless metrics
youtube_short_link = re.compile(r".*youtube\.com/shorts/([\w\-]{11}).*", flags=re.ASCII)
youtube_short_repl = r"https://youtu.be/\1"


@dp.message_handler()
async def youtube_shorts(message: types.Message):
    for link in extract_links(message):
        result, subs = youtube_short_link.subn(youtube_short_repl, link)
        if subs != 0:
            await message.reply(
                f"Sorry, I hate YouTube Shorts.\nHere's your normal video:\n{result}",
                disable_web_page_preview=True,
            )
