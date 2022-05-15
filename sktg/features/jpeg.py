import datetime
from pathlib import Path
from typing import Generator, Union

import PIL.Image

from .. import persistance
from ..telegram import *

check_mark = "✅"

# todo: actual compression


@persistance.create_table
class CachedPhotoSize(persistance.BaseModel):
    chat_id = persistance.IntegerField()
    message_id = persistance.IntegerField()
    width = persistance.IntegerField()
    height = persistance.IntegerField()
    file_id = persistance.TextField()
    # todo: deletion
    timestamp = persistance.DateTimeField(default=datetime.datetime.utcnow)


PhotoSize = Union[types.PhotoSize, CachedPhotoSize]


def size_of_photosize(photosize: PhotoSize) -> int:
    return photosize.width * photosize.height


def get_photosizes_from_message(message: types.Message) -> list[types.PhotoSize] | None:
    if message.photo:
        return sorted(message.photo, key=size_of_photosize, reverse=True)
    elif message.reply_to_message:
        return get_photosizes_from_message(message.reply_to_message)


def get_cached_photosizes(chat_id: int, message_id: int) -> list[CachedPhotoSize]:
    return sorted(
        CachedPhotoSize.select().where(
            (CachedPhotoSize.chat_id == chat_id)
            & (CachedPhotoSize.message_id == message_id)
        ),
        key=size_of_photosize,
        reverse=True,
    )


def resolution_buttons(
    photosizes: list[PhotoSize], selected: int
) -> Generator[types.InlineKeyboardButton, None, None]:
    for i, photo_size in enumerate(photosizes):
        yield types.InlineKeyboardButton(
            text=(check_mark if i == selected else "")
            + f"{photo_size.width}x{photo_size.height}",
            callback_data=f"jpeg_res_{i}",
        )


def keyboard(
    photosizes: list[PhotoSize], selected_resolution: int
) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup().row(
        *resolution_buttons(photosizes, selected_resolution)
    )


@command("jpeg", description="Сожми меня жпегом, братан")
async def jpeg_init(message: types.Message):
    if photosizes := get_photosizes_from_message(message):
        message = await message.reply_photo(
            photosizes[0].file_id,
            reply_markup=keyboard(photosizes, selected_resolution=0),
        )
        for photosize in photosizes:
            CachedPhotoSize.create(
                chat_id=message.chat.id,
                message_id=message.message_id,
                width=photosize.width,
                height=photosize.height,
                file_id=photosize.file_id,
            )
    else:
        await message.reply("No photo, lol")


def temp_file_name() -> str:
    return datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")


# todo: cache results?
async def compress(photo: CachedPhotoSize, message: types.Message):
    width = photo.width
    height = photo.height
    file = Path("jpeg") / f"{temp_file_name()}.jpg"
    try:
        await message.bot.download_file_by_id(file_id=photo.file_id, destination=file)
        # PIL.Image.open(file).resize(
        #     size=(int(width / 2), int(height / 2)),
        # ).save(file, optimize=True, quality=10)
        # PIL.Image.open(file).resize(
        #     size=(width, height),
        # ).save(file, optimize=True, quality=10)
        with open(file, "rb") as f:
            return await message.edit_media(media=types.InputMediaPhoto(f))
    finally:
        file.unlink(missing_ok=True)


@dp.callback_query_handler(lambda cq: cq.data and cq.data.startswith("jpeg"))
async def jpeg(cq: types.CallbackQuery):
    try:
        message = cq.message
        selected_resolution = int(cq.data.split("_")[-1])
        photosizes = get_cached_photosizes(message.chat.id, message.message_id)
        message = await compress(photosizes[selected_resolution], message)
        await message.edit_reply_markup(keyboard(photosizes, selected_resolution))
    finally:
        await cq.answer()
