"""Posting a Shroomjak girl in reply to mushrom stickers
https://pbs.twimg.com/media/FGiFOcKXEAY5EX_?format=jpg&name=900x900
"""

import logging
from typing import Iterable

import telegram
import telegram.ext

from .. import config, persistance, tg_utils

blueprint = tg_utils.Blueprint("shrooms")


class StickerEmojiWhitelist(telegram.ext.MessageFilter):
    def __init__(self, *emojis: str):
        self.emojis = emojis

    def filter(self, message: telegram.Message) -> bool | None:
        if message.sticker:
            return message.sticker.emoji in self.emojis


SHROOM_EMOJI_FILTER = StickerEmojiWhitelist("🍄")


@persistance.create_table
class ShroomSticker(persistance.BaseModel):
    file_unique_id = persistance.TextField(unique=True, index=True)


def add_sticker(file_unique_id: str) -> bool:
    return ShroomSticker.get_or_create(file_unique_id=file_unique_id)[1]


def add_stickers(file_unique_ids: Iterable[str]) -> list[bool]:
    with persistance.database.atomic():
        return list(map(add_sticker, file_unique_ids))


@persistance.create_table
class ShroomStickerSet(persistance.BaseModel):
    set_name = persistance.TextField(unique=True, index=True)


def add_sticker_set(set_name: str) -> bool:
    return ShroomStickerSet.get_or_create(set_name=set_name)[1]


@persistance.migration()
def shooms_from_json():
    json_file = config.config_dir / "shrooms.json"
    if json_file.exists():
        import json

        logger = logging.getLogger("Shrooms migration")

        with open(json_file) as f:
            shrooms_data = json.load(f)

        result = add_stickers(shrooms_data.get("stickers", []))
        logger.info(
            f"Found {len(result)} stickers, added {result.count(True)} new to the databse"
        )

        result = list(map(add_sticker_set, shrooms_data.get("sets", [])))
        logger.info(
            f"Found {len(result)} sets, added {result.count(True)} new to the databse"
        )

        json_file.rename(json_file.with_name("shrooms.migrated.json"))


@persistance.migration()
def bot_admins_from_shroom_admins():
    file = config.config_dir / "shroom_admins.txt"
    if file.exists():
        return persistance.add_admins_from_txt(file)


class _ShroomPersistantWhitelist(telegram.ext.MessageFilter):
    def filter(self, message: telegram.Message) -> bool | None:
        sticker: None | telegram.Sticker = message.sticker
        if sticker is not None:
            return bool(
                ShroomSticker.select().where(
                    ShroomSticker.file_unique_id == sticker.file_unique_id
                )
            ) or bool(
                ShroomStickerSet.select().where(
                    ShroomStickerSet.set_name == sticker.set_name
                )
            )


SHROOM_PERSISTANT_FILTER = _ShroomPersistantWhitelist()

SHROOM_GIRL_FILE_ID: str | None = None


@blueprint.command("shroom", output="s")
def send_shroom_girl(_message: telegram.Message, context: telegram.ext.CallbackContext):
    global SHROOM_GIRL_FILE_ID
    if SHROOM_GIRL_FILE_ID is None:
        SHROOM_GIRL_FILE_ID = (
            context.bot.get_sticker_set(name="DPDvT_SandaruKasa").stickers[98].file_id
        )
    return SHROOM_GIRL_FILE_ID


blueprint.add_handler(
    telegram.ext.MessageHandler(
        filters=SHROOM_EMOJI_FILTER | SHROOM_PERSISTANT_FILTER,
        callback=tg_utils.wrap_command_callback(send_shroom_girl),
    )
)


def replied_sticker(message: telegram.Message) -> telegram.Sticker | None:
    if message.reply_to_message is not None:
        return message.reply_to_message.sticker
    return None


# todo: l10n


@blueprint.command("add_shroom", filters=tg_utils.BOT_ADMIN_FILTER)
def add_shroom(message: telegram.Message, context: telegram.ext.CallbackContext):
    if sticker := replied_sticker(message):
        if add_sticker(sticker.file_unique_id):
            return send_shroom_girl(message, context)
        else:
            return message.reply_text("Already added")
    else:
        return message.reply_text("Reply to a shroom, lol")


@blueprint.command("add_shrooms", filters=tg_utils.BOT_ADMIN_FILTER)
def add_shrooms(message: telegram.Message, context: telegram.ext.CallbackContext):
    if sticker := replied_sticker(message):
        if sticker.set_name:
            shroom_set: telegram.StickerSet = context.bot.get_sticker_set(
                name=sticker.set_name
            )
            shrooms = tuple(file.file_unique_id for file in shroom_set.stickers)
        else:
            shrooms = [sticker.file_unique_id]
        result = add_stickers(shrooms)
        return send_shroom_girl(message, context).reply_text(
            f"{result.count(True)} new shrooms added"
        )
    else:
        return message.reply_text("Reply to a shroom sticker set, lol")


@blueprint.command("add_shroomset", "add_mycelium", filters=tg_utils.BOT_ADMIN_FILTER)
def add_shroomset(message: telegram.Message, context: telegram.ext.CallbackContext):
    if sticker := replied_sticker(message):
        if sticker.set_name:
            if add_sticker_set(sticker.set_name):
                return send_shroom_girl(message, context)
            else:
                return message.reply_text("Already added")
        else:
            return message.reply_text("It's standalone sticker")
    else:
        return message.reply_text("Reply to a shroom sticker set, lol")
