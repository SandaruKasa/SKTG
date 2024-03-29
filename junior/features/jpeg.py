import datetime
import logging
from typing import Generator, Union

import PIL.Image

from sktg import config, persistence
from sktg.telegram import *

from .. import scheduler

ROUTER = Router(name="jpeg")

CHECK_MARK = "✅"
NOW = datetime.datetime.utcnow
CACHE_TTL = datetime.timedelta(days=1)
logger = logging.getLogger(__name__)


@persistence.create_table
class JpegSession(persistence.BaseModel):
    id = persistence.PrimaryKeyField()
    chat_id = persistence.IntegerField()
    message_id = persistence.IntegerField()
    user_id = persistence.IntegerField()
    timestamp = persistence.DateTimeField(default=NOW)


def get_session(message: types.Message) -> JpegSession | None:
    return JpegSession.get_or_none(
        JpegSession.chat_id == message.chat.id,
        JpegSession.message_id == message.message_id,
    )


@persistence.create_table
class CachedOriginal(persistence.BaseModel):
    session = persistence.peewee.ForeignKeyField(
        model=JpegSession, backref="originals", on_delete="CASCADE"
    )
    width = persistence.IntegerField()
    height = persistence.IntegerField()
    file_id = persistence.TextField()


@persistence.create_table
class CachedJpeg(persistence.BaseModel):
    session = persistence.peewee.ForeignKeyField(
        model=JpegSession, backref="results", on_delete="CASCADE"
    )
    width = persistence.IntegerField()
    height = persistence.IntegerField()
    compression_rate = persistence.IntegerField()
    file_id = persistence.TextField()


@scheduler.job(interval=CACHE_TTL / 2)
def prune_cache():
    logger.debug("Prunning jpeg cache...")
    with persistence.database, persistence.database.atomic():
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
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            resolution_buttons(photosizes, selected_resolution),
            compression_rate_buttons(selected_compression),
        ]
    )


@ROUTER.message(
    create_command(
        names=["jpeg", "jpg"],
        description="Сожми меня жпегом, братан",
    )
)
async def jpeg_command_handler(user_message: types.Message):
    photosizes = get_photosizes(user_message)
    if not photosizes:
        return await user_message.reply(
            gettext("Reply with this command to a photo you want to compress")
        )

    biggest_photosize = photosizes[0]
    bot_message = await user_message.reply_photo(
        photo=biggest_photosize.file_id,
        reply_markup=keyboard(
            photosizes,
            selected_resolution=0,
            selected_compression=0,
        ),
    )
    with persistence.database, persistence.database.atomic():
        session = JpegSession.create(
            chat_id=bot_message.chat.id,
            message_id=bot_message.message_id,
            user_id=user_message.from_user.id,
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
            width=biggest_photosize.width,
            height=biggest_photosize.height,
            compression_rate=0,
            file_id=biggest_photosize.file_id,
        )


async def compress(
    bot: Bot,
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
            media=types.InputMediaPhoto(media=cached.file_id),
            chat_id=session.chat_id,
            message_id=session.message_id,
            reply_markup=new_keyboard,
        )

    file = config.get_temp_file_path().with_suffix(".jpg")
    try:
        await bot.download(file=original.file_id, destination=file)
        PIL.Image.open(file).save(
            file,
            optimize=True,
            quality=[100, 10, 5, 1][compression_rate],
        )
        result = await bot.edit_message_media(
            media=types.InputMediaPhoto(media=types.BufferedInputFile.from_file(file)),
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


async def jpeg_callback_body(cq: types.CallbackQuery) -> str:
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
        with persistence.database:
            if session := get_session(message):
                if session.user_id != cq.from_user.id:
                    return gettext("Sorry, this button is not for you")
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
                await message.edit_reply_markup()
                return gettext(
                    "Sorry, this menu is too old.\n"
                    "Please, try using the /jpeg command instead."
                )

    except exceptions.TelegramRetryAfter as e:
        return ngettext(
            "Not so fast! Retry after {} second",
            "Not so fast! Retry after {} seconds",
            e.timeout,
        ).format(e.timeout)
    # This used to be a MessageNotModified exception
    # TODO: open a PR to bring it back?
    except exceptions.TelegramBadRequest as e:
        if "message is not modified" not in e.message:
            raise


@ROUTER.callback_query(F.data.startswith("jpeg"))
async def jpeg_callback_handler(cq: types.CallbackQuery):
    text = None
    try:
        text = await jpeg_callback_body(cq)
    finally:
        await cq.answer(text)
