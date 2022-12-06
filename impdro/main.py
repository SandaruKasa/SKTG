import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import aiogram
from aiogram import types
from aiogram.utils.markdown import hbold, hitalic, hlink

import tokens

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=r"%Y-%m-%dT%H-%M-%S",
)

bot = aiogram.Bot(token=tokens.token)
dispatcher = aiogram.Dispatcher(bot)


def command(name: str, *aliases: str, **kwargs):
    return dispatcher.message_handler(commands=[name, *aliases], **kwargs)


@command("start", "help", "send")
async def farewell(message: types.Message):
    await message.reply(
        "К сожалению, я больше не работаю.\n"
        "Sadly, I do not do anything anymore.\n" + tokens.statement
    )


@command("goodbye")
async def goodbye(message: types.Message):
    await message.reply(tokens.statement)


def read_json(file: Path):
    with open(file) as f:
        return json.load(f)


CHAT_ID = int
USER_ID = int
COUNT = int


@dataclass
class ChatStatsEntry:
    user: types.User
    count: COUNT


@dataclass
class UserStatsEntry:
    chat: types.Chat
    count: COUNT


DATA_DIR = Path("data")

STATS: dict[CHAT_ID, dict[USER_ID, COUNT]] = {
    CHAT_ID(file.stem): {USER_ID(k): v for k, v in read_json(file).items()}
    for file in (DATA_DIR / "counters").iterdir()
}

USERS: dict[USER_ID, types.User] = {
    user.id: user
    for user in (
        types.User(**{"id": USER_ID(k), **v})
        for k, v in read_json(DATA_DIR / "users.json").items()
    )
}


CHATS: dict[CHAT_ID, types.Chat] = {
    chat.id: chat
    for chat in (
        types.Chat(**{"id": CHAT_ID(k), **v})
        for k, v in read_json(DATA_DIR / "chats.json").items()
    )
}


def get_user_top(user_id: USER_ID) -> list[UserStatsEntry]:
    result = [
        UserStatsEntry(CHATS[chat_id], count)
        for chat_id in STATS.keys()
        if (count := STATS[chat_id].get(user_id))
    ]
    result.sort(key=lambda entry: entry.count, reverse=True)
    return result


def get_chat_top(chat_id: int) -> list[ChatStatsEntry]:
    results = [
        ChatStatsEntry(USERS[user_id], count)
        for user_id, count in STATS[chat_id].items()
    ]
    results.sort(key=lambda entry: entry.count, reverse=True)
    return results


def is_private(chat: types.Chat) -> bool:
    return chat.type == types.ChatType.PRIVATE


def get_top_entries(chat: types.Chat) -> Generator[str, None, None]:
    if is_private(chat):
        for place, entry in enumerate(get_user_top(chat.id), start=1):
            yield "{place}. {count} — {chat}".format(
                place=place,
                count=hbold(entry.count),
                chat=hitalic(entry.chat.full_name),
            )
    else:
        for place, entry in enumerate(get_chat_top(chat.id), start=1):
            yield "{place}. {user}: {count}".format(
                place=place,
                user=hlink(
                    entry.user.full_name,
                    f"tg://user?id={entry.user.id}",
                ),
                count=entry.count,
            )


@command("top")
async def top(message: types.Message):
    chat = message.chat
    top = get_top_entries(chat)
    if top:
        if is_private(chat):
            header = (
                "Top of the chats you have been active in:\n"
                "Топ чатов, в которых ты был активен:\n"
            )
        else:
            chat_name = hitalic(message.chat.title)
            header = (
                f"Top active members of {chat_name}:\n"
                f"Самые активные участники {chat_name}:\n"
            )

        await message.reply("\n".join((header, *top)), parse_mode=types.ParseMode.HTML)
    else:
        await message.reply("No data. / Нет данных.")


@command("database")
async def resources(message: types.Message):
    await message.reply_media_group(
        [types.InputMediaDocument(file_id) for file_id in tokens.database_archives]
    )


if __name__ == "__main__":
    aiogram.executor.start_polling(dispatcher=dispatcher)
