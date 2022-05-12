"""Posting a Shroomjak girl in reply to mushrom stickers
https://pbs.twimg.com/media/FGiFOcKXEAY5EX_?format=jpg&name=900x900
"""

from typing import Iterable

from .. import persistance
from ..telegram import *


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


@dp.message_handler(shroom_stickerset_filter, content_types=types.ContentTypes.STICKER)
@dp.message_handler(shroom_sticker_filter, content_types=types.ContentTypes.STICKER)
@dp.message_handler(shroom_emoji_filter, content_types=types.ContentTypes.STICKER)
@dp.message_handler(commands=["shroom"])
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


@dp.message_handler(bot_admin_filter, commands=["add_shroom"])
async def add_shroom(message: types.Message):
    if sticker := replied_sticker(message):
        if add_sticker(sticker.file_unique_id):
            return await reply_with_shroom_girl(message)
        else:
            return await message.reply("Already added")
    else:
        return await message.reply("Reply to a shroom, lol")


@dp.message_handler(bot_admin_filter, commands=["add_shrooms"])
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


@dp.message_handler(bot_admin_filter, commands=["add_shroomset", "add_mycelium"])
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
