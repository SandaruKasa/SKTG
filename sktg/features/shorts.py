import re
from typing import Generator

from ..telegram import *


def extract_links(message: types.Message) -> Generator[str, None, None]:
    # For the love of God, why do you have to treat captions and text differently?
    # They behave exactly the same in the API and both represent the text part of the message.
    # WHY WOULD YOU NEED TO PUT THEM IN DIFFERENT PLACES?
    # SO THAT API USERS HAVE TO WRITE MORE IF'S?
    for entity in message.entities or message.caption_entities:
        if entity.type == types.MessageEntityType.TEXT_LINK:
            yield entity.url
        elif entity.type == types.MessageEntityType.URL:
            yield entity.get_text(message.text or message.caption)


# [\w] gives [0-9a-zA-Z_] in ASCII mode
# `.*` in the beginning to prevent www.youtu.be from happening
# `.*` in the end to get rid of ?feature=share and other useless metrics
youtube_short_link = re.compile(r".*youtube\.com/shorts/([\w\-]{11}).*", flags=re.ASCII)
youtube_short_repl = r"https://youtu.be/\1"


@dispatcher.message_handler(content_types=types.ContentTypes.ANY)
async def youtube_shorts(message: types.Message):
    result = []
    for link in extract_links(message):
        substituted, subs = youtube_short_link.subn(youtube_short_repl, link)
        if subs != 0:
            result.append(substituted)
    if result:
        await message.reply(
            "Sorry, I hate YouTube Shorts.\nHere's your video in the normal format:\n"
            + "\n".join(result),
            disable_web_page_preview=True,
        )
    raise aiogram.dispatcher.handler.SkipHandler()  # so that it doesn't block other features
