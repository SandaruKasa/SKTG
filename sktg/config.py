"""Parsing configs and storing tokens/uptimes
"""

import datetime
import logging
import os
from pathlib import Path

datetime_fmt = r"%Y-%m-%dT%H-%M-%S"


config_dir = Path("config")
assert config_dir.is_dir(), "Config directory doesn't exist"


token = os.getenv("TOKEN")
if token is None:
    with open(config_dir / "token.txt") as f:
        token = f.read().strip()


startup_time: None | datetime.datetime = None


def get_uptime(bot_id: int) -> datetime.timedelta | None:
    """Get the uptime of a bot

    ``set_startup_time`` must have been called for the given ``bot_id`` prior to this call.

    Args:
        bot_id (int): Telegram's user id fot the bot

    Returns:
        datetime.timedelta | None: timedelta representing the uptime of the bot with the given id
                                   (or None if ``set_startup_time``) wasn't called
    """
    if startup_time is not None:
        return datetime.datetime.now() - startup_time
    else:
        return None
