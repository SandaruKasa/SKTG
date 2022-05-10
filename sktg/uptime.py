"""Parsing configs and storing tokens/uptimes
"""

import datetime

_startup_time: dict[int, datetime.datetime] = {}

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
