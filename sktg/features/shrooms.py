"""Posting a Shroomjak girl in reply to mushrom stickers
https://pbs.twimg.com/media/FGiFOcKXEAY5EX_?format=jpg&name=900x900
"""

import telegram.ext
from sktg.persistance import *
from sktg.utils import *

blueprint = Blueprint("shrooms")


class StickerEmojiWhitelist(telegram.ext.MessageFilter):
    def __init__(self, *emojis: str):
        self.emojis = emojis

    def filter(self, message: telegram.Message) -> bool | None:
        if message.sticker:
            return message.sticker.emoji in self.emojis


shroom_emoji_filter = StickerEmojiWhitelist("🍄")
shroom_whitelist = StickerWhitelistFilter(persistance_dir / "shrooms.json")
shroom_admins = UserWhitelistFilter(persistance_dir / "shroom_admins.txt")

shroom_girl_id: str | None = None


@blueprint.command("shroom", output="s")
def send_shroom_girl(_message: telegram.Message, context: telegram.ext.CallbackContext):
    global shroom_girl_id
    if shroom_girl_id is None:
        shroom_girl_id = (
            context.bot.get_sticker_set(name="DPDvT_SandaruKasa").stickers[98].file_id
        )
    return shroom_girl_id


blueprint.add_handler(
    telegram.ext.MessageHandler(
        filters=shroom_whitelist | shroom_emoji_filter,
        callback=wrap_command_callback(send_shroom_girl),
    )
)


def replied_sticker(message: telegram.Message) -> telegram.Sticker | None:
    if message.reply_to_message is not None:
        return message.reply_to_message.sticker
    return None


# todo: l10n


@blueprint.command("add_shroom", filters=shroom_admins)
def add_shroom(message: telegram.Message, context: telegram.ext.CallbackContext):
    if sticker := replied_sticker(message):
        if shroom_whitelist.add_stickers(sticker.file_unique_id)[0]:
            return send_shroom_girl(message, context)
        else:
            return message.reply_text("Already added")
    else:
        return message.reply_text("Reply to a shroom, lol")


@blueprint.command("add_shrooms", filters=shroom_admins)
def add_shrooms(message: telegram.Message, context: telegram.ext.CallbackContext):
    if sticker := replied_sticker(message):
        if sticker.set_name:
            shroom_set: telegram.StickerSet = context.bot.get_sticker_set(
                name=sticker.set_name
            )
            shrooms = tuple(file.file_unique_id for file in shroom_set.stickers)
        else:
            shrooms = [sticker.file_unique_id]
        result = shroom_whitelist.add_stickers(*shrooms)
        return send_shroom_girl(message, context).reply_text(
            f"{result.count(True)} new shrooms added"
        )
    else:
        return message.reply_text("Reply to a shroom sticker set, lol")


@blueprint.command("add_shroomset", "add_mycelium", filters=shroom_admins)
def add_shroomset(message: telegram.Message, context: telegram.ext.CallbackContext):
    if sticker := replied_sticker(message):
        if sticker.set_name:
            if shroom_whitelist.add_set(sticker.set_name):
                return send_shroom_girl(message, context)
            else:
                return message.reply_text("Already added")
        else:
            return message.reply_text("It's standalone sticker")
    else:
        return message.reply_text("Reply to a shroom sticker set, lol")
