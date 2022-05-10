"""Parsing configs and storing tokens/uptimes
"""

import datetime
import pathlib

config_dir = pathlib.Path("config").resolve()
assert config_dir.is_dir(), "Config directory not found"

_token_file = config_dir / "token.txt"

_startup_time: dict[int, datetime.datetime] = {}


def get_token() -> str:
    """Fetch bot token from the config/token.txt file

    Returns:
        str: The token of the bot in the 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew1 format
    """
    with open(_token_file) as f:
        return f.read().strip()


def set_startup_time(bot_id: int):
    """Sets the startup time of the bot with the given id to datetime.datetime.now()

    Args:
        bot_id (int): Telegram's user id fot the bot
    """
    _startup_time[bot_id] = datetime.datetime.now()


def get_uptime(bot_id: int) -> datetime.timedelta | None:
    """Get the uptime of a bot

    ``set_startup_time`` must have been called for the given ``bot_id`` prior to this call.

    Args:
        bot_id (int): Telegram's user id fot the bot

    Returns:
        datetime.timedelta | None: timedelta representing the uptime of the bot with the given id
                                   (or None if ``set_startup_time``) wasn't called
    """
    startup_time = _startup_time.get(bot_id)
    if startup_time is not None:
        return datetime.datetime.now() - startup_time
    else:
        return None
