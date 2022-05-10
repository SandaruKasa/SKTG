"""Basic functionality I would like all the bots to have.
Added to a bot by the ``create_bot`` function of the module by default.
"""
import json
import logging

import sktg.uptime
import telegram.ext
from sktg.utils import Blueprint


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
    logging.getLogger(f"{context.bot.username}").debug(
        "UPDATE:\n%s", format_update(update)
    )


class LoggingHandler(telegram.ext.Handler):
    def __init__(self):
        super().__init__(callback=log_update)

    def check_update(self, update: object) -> bool:
        return True


base = Blueprint("base")
base.add_handler(LoggingHandler())


@base.command(
    "source", "opensource", "github", output="t", disable_web_page_preview=True
)
def github_link():
    return "https://github.com/SandaruKasa/SKTG/tree/dev"


@base.command("shrug", output="t")
def shrug():
    return r"¯\_(ツ)_/¯"


@base.command("uptime", output="t")
def uptime(_message: telegram.Message, context: telegram.ext.CallbackContext):
    uptime = sktg.uptime.get_uptime(context.bot.id)
    if uptime is None:
        return "Unkown"
    else:
        # stripping microseconds
        return str(uptime).split(".")[0]
