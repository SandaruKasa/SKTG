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


@persistance.migration()
def add_compression_rate():
    persistance.database.execute_sql("DROP TABLE IF EXISTS cachedphotosize;")


@persistance.create_table
class JpegSession(persistance.BaseModel):
    id = persistance.PrimaryKeyField()
    chat_id = persistance.IntegerField()
    message_id = persistance.IntegerField()
    timestamp = persistance.DateTimeField(default=NOW)


def get_session(message: types.Message) -> JpegSession | None:
    return JpegSession.get_or_none(
        JpegSession.chat_id == message.chat.id,
        JpegSession.message_id == message.message_id,
    )


@persistance.create_table
class CachedOriginal(persistance.BaseModel):
    session = persistance.peewee.ForeignKeyField(
        model=JpegSession, backref="originals", on_delete="CASCADE"
    )
    width = persistance.IntegerField()
    height = persistance.IntegerField()
    file_id = persistance.TextField()


@persistance.create_table
class CachedJpeg(persistance.BaseModel):
    session = persistance.peewee.ForeignKeyField(
        model=JpegSession, backref="results", on_delete="CASCADE"
    )
    width = persistance.IntegerField()
    height = persistance.IntegerField()
    compression_rate = persistance.IntegerField()
    file_id = persistance.TextField()


@scheduler.job(interval=CACHE_TTL / 2)
def prune_cache():
    logger.debug("Prunning jpeg cache...")
    with persistance.database, persistance.database.atomic():
        JpegSession.delete().where(JpegSession.timestamp < NOW() - CACHE_TTL).execute()
    logger.debug("Jpeg cache prunned")


PhotoSize = Union[types.PhotoSize, CachedOriginal]


def size_of_photosize(photosize: PhotoSize) -> int:
    return photosize.width * photosize.height


def get_photosizes(message: types.Message) -> list[types.PhotoSize] | None:
    if message.photo:
        return sorted(message.photo, key=size_of_photosize, reverse=True)
    elif message.reply_to_message:
        return get_photosizes(message.reply_to_message)


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
    photosizes = get_photosizes(message)
    if not photosizes:
        return await message.reply("No photo, lol")

    biggest = photosizes[0]
    message = await message.reply_photo(
        photo=biggest.file_id,
        reply_markup=keyboard(
            photosizes,
            selected_resolution=0,
            selected_compression=0,
        ),
    )
    with persistance.database, persistance.database.atomic():
        session = JpegSession.create(
            chat_id=message.chat.id, message_id=message.message_id
        )
        for photosize in photosizes:
            CachedOriginal.create(
                session=session,
                width=photosize.width,
                height=photosize.height,
                file_id=photosize.file_id,
            )
        CachedJpeg.create(
            session=session,
            width=biggest.width,
            height=biggest.height,
            compression_rate=0,
            file_id=biggest.file_id,
        )
    return message


def temp_file_name() -> str:
    return datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")


async def compress(
    bot: aiogram.Bot,
    session: JpegSession,
    original: CachedOriginal,
    compression_rate: int,
    new_keyboard: types.InlineKeyboardMarkup,
):
    if cached := CachedJpeg.get_or_none(
        CachedJpeg.session == session,
        CachedJpeg.width == original.width,
        CachedJpeg.height == original.height,
        CachedJpeg.compression_rate == compression_rate,
    ):
        return await bot.edit_message_media(
            media=types.InputMediaPhoto(cached.file_id),
            chat_id=session.chat_id,
            message_id=session.message_id,
            reply_markup=new_keyboard,
        )

    file = Path("jpeg") / f"{temp_file_name()}.jpg"
    try:
        await bot.download_file_by_id(file_id=original.file_id, destination=file)
        PIL.Image.open(file).save(
            file,
            optimize=True,
            quality=[100, 10, 5, 1][compression_rate],
        )
        with open(file, "rb") as f:
            result = await bot.edit_message_media(
                media=types.InputMediaPhoto(f),
                chat_id=session.chat_id,
                message_id=session.message_id,
                reply_markup=new_keyboard,
            )
        CachedJpeg.create(
            session=session,
            width=original.width,
            height=original.height,
            compression_rate=compression_rate,
            file_id=get_photosizes(result)[0].file_id,
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
        with persistance.database:
            if session := get_session(message):
                originals = sorted(
                    session.originals,
                    key=size_of_photosize,
                    reverse=True,
                )
                await compress(
                    bot=cq.bot,
                    session=session,
                    original=originals[selected_resolution],
                    compression_rate=selected_compression,
                    new_keyboard=keyboard(
                        originals, selected_resolution, selected_compression
                    ),
                )
            else:
                cq_answer_text = (
                    "This message is too old, sorry.\nTry using the /jpeg command."
                )
                await message.edit_reply_markup()
    except aiogram.exceptions.RetryAfter as e:
        cq_answer_text = f"Not so fast! Retry after {e.timeout} seconds"
    except aiogram.exceptions.MessageNotModified as e:
        pass
    finally:
        await cq.answer(cq_answer_text)
