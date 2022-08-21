"""Posting a Shroomjak girl in reply to mushroom stickers
https://pbs.twimg.com/media/FGiFOcKXEAY5EX_?format=jpg&name=900x900
"""

from typing import Iterable

from sktg import persistence
from sktg.telegram import *


@persistence.create_table
class ShroomSticker(persistence.BaseModel):
    file_unique_id = persistence.TextField(unique=True, index=True)


def add_sticker(file_unique_id: str) -> bool:
    return ShroomSticker.get_or_create(file_unique_id=file_unique_id)[1]


def add_stickers(file_unique_ids: Iterable[str]) -> list[bool]:
    with persistence.database.atomic():
        return list(map(add_sticker, file_unique_ids))


@persistence.create_table
class ShroomStickerSet(persistence.BaseModel):
    set_name = persistence.TextField(unique=True, index=True)


def add_sticker_set(set_name: str) -> bool:
    return ShroomStickerSet.get_or_create(set_name=set_name)[1]


def shroom_emoji_filter(message: types.Message) -> bool:
    return message.sticker and message.sticker.emoji == "🍄"


def shroom_sticker_filter(message: types.Message) -> bool:
    return message.sticker and ShroomSticker.select().where(
        ShroomSticker.file_unique_id == message.sticker.file_unique_id
    )


def shroom_stickerset_filter(message: types.Message) -> bool:
    return message.sticker and ShroomStickerSet.select().where(
        ShroomStickerSet.set_name == message.sticker.set_name
    )


SHROOM_GIRL_FILE_ID: str | None = None


@dispatcher.message_handler(
    shroom_stickerset_filter, content_types=types.ContentTypes.STICKER
)
@dispatcher.message_handler(
    shroom_sticker_filter, content_types=types.ContentTypes.STICKER
)
@dispatcher.message_handler(
    shroom_emoji_filter, content_types=types.ContentTypes.STICKER
)
@command("shroom")
async def reply_with_shroom_girl(message: types.Message):
    global SHROOM_GIRL_FILE_ID
    if SHROOM_GIRL_FILE_ID is None:
        SHROOM_GIRL_FILE_ID = (
            (await bot.get_sticker_set(name="DPDvT_SandaruKasa")).stickers[98].file_id
        )
    return await message.reply_sticker(sticker=SHROOM_GIRL_FILE_ID)


def replied_sticker(message: types.Message) -> types.Sticker | None:
    if message.reply_to_message is not None:
        return message.reply_to_message.sticker
    return None


# todo: i18n & l10n


@command("add_shroom", filters=(bot_admin_filter,))
async def add_shroom(message: types.Message):
    if sticker := replied_sticker(message):
        if add_sticker(sticker.file_unique_id):
            return await reply_with_shroom_girl(message)
        else:
            return await message.reply("Already added")
    else:
        return await message.reply("Reply to a shroom, lol")


@command("add_shrooms", filters=(bot_admin_filter,))
async def add_shrooms(message: types.Message):
    if sticker := replied_sticker(message):
        if sticker.set_name:
            shroom_set = await bot.get_sticker_set(name=sticker.set_name)
            shrooms = tuple(file.file_unique_id for file in shroom_set.stickers)
        else:
            shrooms = [sticker.file_unique_id]
        result = add_stickers(shrooms)
        message = await reply_with_shroom_girl(message)
        return await message.reply(f"{result.count(True)} new shrooms added")
    else:
        return await message.reply("Reply to a shroom sticker set, lol")


@command("add_shroomset", "add_mycelium", filters=(bot_admin_filter,))
async def add_shroomset(message: types.Message):
    if sticker := replied_sticker(message):
        if sticker.set_name:
            if add_sticker_set(sticker.set_name):
                return await reply_with_shroom_girl(message)
            else:
                return await message.reply("Already added")
        else:
            return await message.reply("It's standalone sticker")
    else:
        return await message.reply("Reply to a shroom sticker set, lol")
