import re
from typing import Generator

from util.telegram import *


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


def convert_links(message: types.Message) -> Generator[str, None, None]:
    for link in extract_links(message):
        substituted, subs = youtube_short_link.subn(youtube_short_repl, link)
        if subs != 0:
            yield substituted


@command(
    "shorts", "short", "fix", description="Convert YouTube Shorts into normal videos"
)
async def youtube_shorts(message: types.Message):
    result = list(convert_links(message))
    if not result and message.reply_to_message:
        result = list(convert_links(message.reply_to_message))

    if result:
        await message.reply(
            gettext("Here you are:\n{}").format("\n".join(result)),
            disable_web_page_preview=True,
        )
    else:
        await message.reply(
            gettext(
                "Send this command as a reply to a message with a YouTube Shorts link "
                "or paste the link after the command."
            )
        )
