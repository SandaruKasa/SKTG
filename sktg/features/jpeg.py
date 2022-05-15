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
    file_id = persistance.TextField()
    timestamp = persistance.DateTimeField(default=NOW)


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
            text=(CHECK_MARK if i == selected else "")
            + f"{photo_size.width}x{photo_size.height}",
            callback_data=f"jpeg_res_{i}",
        )


def compression_level_buttons(
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
        .row(*compression_level_buttons(selected_compression))
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
                )
    else:
        await message.reply("No photo, lol")


def temp_file_name() -> str:
    return datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")


# todo: cache results?
async def compress(
    message: types.Message, photo: CachedPhotoSize, compression_rate: int
):
    file = Path("jpeg") / f"{temp_file_name()}.jpg"
    try:
        await message.bot.download_file_by_id(file_id=photo.file_id, destination=file)
        PIL.Image.open(file).save(
            file,
            optimize=True,
            quality=[100, 10, 5, 1][compression_rate],
        )
        with open(file, "rb") as f:
            return await message.edit_media(media=types.InputMediaPhoto(f))
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
        photosizes = get_cached_photosizes(message.chat.id, message.message_id)
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
    finally:
        await cq.answer(cq_answer_text)
