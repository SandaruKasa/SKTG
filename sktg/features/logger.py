"""Logging functionality for bots.
Included in the ``base`` blueprint by default.
Named ``logger`` and not ``logging`` to avoid a name conflict.
"""
# todo: merge the blueprint into base and moving logging utils into a separate module
#       https://github.com/irdkwmnsb/proga-bot/blob/main/progabot/logger.py
# todo: rework this to use some sort of an env variable to determine logging level
#       https://stackoverflow.com/questions/14058453


import datetime
import json
import logging
import pathlib

import telegram.ext

from sktg.utils import Blueprint

logger = Blueprint("logger")

logging_dir = pathlib.Path("logs").resolve()
logging_dir.mkdir(exist_ok=True)

logging.basicConfig(
    filename=logging_dir / f"{datetime.datetime.now().isoformat()}.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def format_update(update: telegram.Update | object) -> str:
    """Format an update for logging or pretty-printing.
    Takes either a ``telegram.Update`` or just any ``object``, because this is what is implied to be a possible type by
    https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.handler.html#telegram.ext.Handler.check_update


    Args:
        update (telegram.Update | object): the update to format

    Returns:
        str: a string with the json representation for ``telegram.Update``, the default string representation otherwise
    """
    if isinstance(update, telegram.Update):
        return json.dumps(update.to_dict(), indent=4, ensure_ascii=False)
    else:
        return str(update)


def log_update(update: telegram.Update | object, context: telegram.ext.CallbackContext):
    logging.getLogger(f"{context.bot.username}: UPDATE")\
        .info("\n%s", format_update(update))


class LoggingHandler(telegram.ext.Handler):
    """The handler that selects updates to log."""

    def __init__(self, callback=format_update):
        super().__init__(callback=callback)

    def check_update(self, update) -> bool:
        """Currently, is set to log all updates except new/edited messages/posts."""
        if isinstance(update, telegram.Update):
            return not (update.message or update.edited_message or update.channel_post or update.edited_channel_post)
        else:
            return True


logger.add_handler(LoggingHandler())
