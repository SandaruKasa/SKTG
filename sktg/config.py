"""Parsing configs and storing tokens/uptimes
"""

import datetime
import json
import pathlib

config_dir = pathlib.Path("config").resolve()
assert config_dir.is_dir(), "Config directory not found"

_token_file = config_dir / "tokens.json"
_tokens: dict[str, str] = json.load(open(_token_file))

_startup_time: dict[int, datetime.datetime] = {}


def get_token(bot_name: str) -> str:
    """Fetch bot token from the tokens.json file

    Args:
        bot_name (str): Local name of the bot, as provided in the tokens.json file

    Returns:
        str: The token of the bot in the 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew1 format
    """
    return _tokens[bot_name]


def set_startup_time(bot_id: int):
    """Sets the startup time of the bot with the given id to datetime.datetime.now()

    Args:
        bot_id (int): Telegram's user id fot the bot
    """
    _startup_time[bot_id] = datetime.datetime.now()


def get_uptime(bot_id: int) -> datetime.timedelta:
    """Get the uptime of a bot

    ``set_startup_time`` must have been called for the given ``bot_id`` prior to this call.

    Args:
        bot_id (int): Telegram's user id fot the bot

    Returns:
        datetime.timedelta: datetime.timedelta representing the uptime of the bot with the given id
    """
    return datetime.datetime.now() - _startup_time[bot_id]
