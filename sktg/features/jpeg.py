import datetime
import logging
from pathlib import Path
from typing import Generator, Union

import PIL.Image

from .. import persistance, scheduler
from ..telegram import *

CHECK_MARK = "✅"
NOW = datetime.datetime.utcnow
CACHE_TTL = datetime.timedelta(days=1)
logger = logging.getLogger(__name__)


@persistance.create_table
class CachedPhotoSize(persistance.BaseModel):
    chat_id = persistance.IntegerField()
    message_id = persistance.IntegerField()
    width = persistance.IntegerField()
    height = persistance.IntegerField()
    compression_rate = persistance.IntegerField()
    file_id = persistance.TextField()
    timestamp = persistance.DateTimeField(default=NOW)


@persistance.migration()
def add_compression_rate():
    CachedPhotoSize.drop_table()
    CachedPhotoSize.create_table()


@scheduler.job(interval=CACHE_TTL)
def prune_photosizes_cache():
    logger.info("Removing outdated CachedPhotoSize's...")
    with persistance.database.atomic():
        CachedPhotoSize.delete().where(
            CachedPhotoSize.timestamp < NOW() - CACHE_TTL
        ).execute()
    logger.info("Outdated CachedPhotoSize's removed")


PhotoSize = Union[types.PhotoSize, CachedPhotoSize]


def size_of_photosize(photosize: PhotoSize) -> int:
    return photosize.width * photosize.height


def get_photosizes_from_message(message: types.Message) -> list[types.PhotoSize] | None:
    if message.photo:
        return sorted(message.photo, key=size_of_photosize, reverse=True)
    elif message.reply_to_message:
        return get_photosizes_from_message(message.reply_to_message)


def resolution_buttons(
    photosizes: list[PhotoSize], selected: int
) -> Generator[types.InlineKeyboardButton, None, None]:
    for i, photo_size in enumerate(photosizes):
        yield types.InlineKeyboardButton(
            text=(CHECK_MARK if i == selected else "")
            + f"{photo_size.width}x{photo_size.height}",
            callback_data=f"jpeg_res_{i}",
        )


def compression_rate_buttons(
    selected: int,
) -> Generator[types.InlineKeyboardButton, None, None]:
    for i in range(4):
        yield types.InlineKeyboardButton(
            text=(CHECK_MARK if i == selected else "") + f"🙈x{i}",
            callback_data=f"jpeg_com_{i}",
        )


def keyboard(
    photosizes: list[PhotoSize], selected_resolution: int, selected_compression: int
) -> types.InlineKeyboardMarkup:
    return (
        types.InlineKeyboardMarkup()
        .row(*resolution_buttons(photosizes, selected_resolution))
        .row(*compression_rate_buttons(selected_compression))
    )


@command("jpeg", description="Сожми меня жпегом, братан")
async def jpeg_init(message: types.Message):
    if photosizes := get_photosizes_from_message(message):
        message = await message.reply_photo(
            photosizes[0].file_id,
            reply_markup=keyboard(
                photosizes,
                selected_resolution=0,
                selected_compression=0,
            ),
        )
        with persistance.database.atomic():
            for photosize in photosizes:
                CachedPhotoSize.create(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    width=photosize.width,
                    height=photosize.height,
                    file_id=photosize.file_id,
                    compression_rate=0,
                )
    else:
        await message.reply("No photo, lol")


def temp_file_name() -> str:
    return datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")


async def compress(
    message: types.Message, photo: CachedPhotoSize, compression_rate: int
):
    if cached := list(
        CachedPhotoSize.select().where(
            (CachedPhotoSize.chat_id == message.chat.id)
            & (CachedPhotoSize.message_id == message.message_id)
            & (CachedPhotoSize.width == photo.width)
            & (CachedPhotoSize.height == photo.height)
            & (CachedPhotoSize.compression_rate == compression_rate)
        )
    ):
        cached = cached[0]
        return await message.edit_media(types.InputMediaPhoto(cached.file_id))

    file = Path("jpeg") / f"{temp_file_name()}.jpg"
    try:
        await message.bot.download_file_by_id(file_id=photo.file_id, destination=file)
        PIL.Image.open(file).save(
            file,
            optimize=True,
            quality=[100, 10, 5, 1][compression_rate],
        )
        with open(file, "rb") as f:
            result = await message.edit_media(media=types.InputMediaPhoto(f))
        CachedPhotoSize.get_or_create(
            chat_id=message.chat.id,
            message_id=message.message_id,
            width=photo.width,
            height=photo.height,
            file_id=get_photosizes_from_message(message)[0].file_id,
            compression_rate=compression_rate,
        )
        return result

    finally:
        file.unlink(missing_ok=True)


def index_of_a_button_that_starts_with_a_check_mark(
    row: list[types.InlineKeyboardButton],
) -> int:
    for i, button in enumerate(row):
        if button.text.startswith(CHECK_MARK):
            return i


@dp.callback_query_handler(lambda cq: cq.data and cq.data.startswith("jpeg"))
async def jpeg(cq: types.CallbackQuery):
    cq_answer_text: str = ""
    try:
        message = cq.message
        __, mode, selected = cq.data.split("_")
        selected = int(selected)
        match mode:
            case "res":
                selected_resolution = selected
                selected_compression = index_of_a_button_that_starts_with_a_check_mark(
                    message.reply_markup.inline_keyboard[1]
                )
            case "com":
                selected_resolution = index_of_a_button_that_starts_with_a_check_mark(
                    message.reply_markup.inline_keyboard[0]
                )
                selected_compression = selected
        photosizes = sorted(
            CachedPhotoSize.select().where(
                (CachedPhotoSize.chat_id == message.chat.id)
                & (CachedPhotoSize.message_id == message.message_id)
                & (CachedPhotoSize.compression_rate == 0)
            ),
            key=size_of_photosize,
            reverse=True,
        )
        if photosizes:
            message = await compress(
                message=message,
                photo=photosizes[selected_resolution],
                compression_rate=selected_compression,
            )
            await message.edit_reply_markup(
                keyboard(photosizes, selected_resolution, selected_compression)
            )
        else:
            cq_answer_text = (
                "This message is too old, sorry.\nTry using the /jpeg command."
            )
            await message.edit_reply_markup()
    except aiogram.exceptions.RetryAfter as e:
        cq_answer_text = f"Not so fast! Retry after {e.timeout} seconds"
    finally:
        await cq.answer(cq_answer_text)
