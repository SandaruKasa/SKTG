from ..telegram import *

import re


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
            await message.reply(result)
