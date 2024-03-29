"""Posting a Shroomjak girl in reply to mushroom stickers
https://pbs.twimg.com/media/FGiFOcKXEAY5EX_?format=jpg&name=900x900
"""

from typing import Iterable

from sktg import persistence
from sktg.telegram import *

ROUTER = Router(name="shrooms")


@persistence.create_table
class ShroomSticker(persistence.BaseModel):
    file_unique_id = persistence.TextField(unique=True, index=True)


def add_sticker(file_unique_id: str) -> bool:
    return ShroomSticker.get_or_create(file_unique_id=file_unique_id)[1]


@persistence.create_table
class ShroomStickerSet(persistence.BaseModel):
    set_name = persistence.TextField(unique=True, index=True)


def add_sticker_set(set_name: str) -> bool:
    return ShroomStickerSet.get_or_create(set_name=set_name)[1]


def shroom_sticker_filter(message: types.Message) -> bool:
    return message.sticker and ShroomSticker.select().where(
        ShroomSticker.file_unique_id == message.sticker.file_unique_id
    )


def shroom_stickerset_filter(message: types.Message) -> bool:
    return message.sticker and ShroomStickerSet.select().where(
        ShroomStickerSet.set_name == message.sticker.set_name
    )


SHROOM_GIRL_FILE_ID: str | None = None


@ROUTER.message(shroom_stickerset_filter)
@ROUTER.message(shroom_sticker_filter)
@ROUTER.message(F.sticker.emoji == "🍄")
@ROUTER.message(filters.Command("shroom"))
async def reply_with_shroom_girl(message: types.Message):
    global SHROOM_GIRL_FILE_ID
    if SHROOM_GIRL_FILE_ID is None:
        sticker_set = await message.bot.get_sticker_set(name="DPDvT_SandaruKasa")
        SHROOM_GIRL_FILE_ID = sticker_set.stickers[98].file_id
    return await message.reply_sticker(sticker=SHROOM_GIRL_FILE_ID)


def replied_sticker(message: types.Message) -> types.Sticker | None:
    if message.reply_to_message is not None:
        return message.reply_to_message.sticker
    return None


@ROUTER.message(filter_admins, filters.Command("add_shroom"))
async def add_shroom(message: types.Message):
    if sticker := replied_sticker(message):
        if add_sticker(sticker.file_unique_id):
            return await reply_with_shroom_girl(message)
        else:
            return await message.reply(gettext("Already added"))
    else:
        return await message.reply(gettext("Reply to a shroom, lol"))


@ROUTER.message(filter_admins, filters.Command("add_shroomset", "add_mycelium"))
async def add_shroomset(message: types.Message):
    if sticker := replied_sticker(message):
        if sticker.set_name:
            if add_sticker_set(sticker.set_name):
                return await reply_with_shroom_girl(message)
            else:
                return await message.reply(gettext("Already added"))
        else:
            return await message.reply(gettext("It's a standalone sticker"))
    else:
        return await message.reply(gettext("Reply to a shroom sticker set, lol"))
