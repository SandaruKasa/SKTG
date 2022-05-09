"""Basic functionality I would like all the bots to have.
Added to a bot by the ``create_bot`` function of the module by default.
"""

import telegram.ext

import sktg.config
from sktg.utils import Blueprint
from .logger import logger

base = Blueprint("base", logger)


@base.command("source", "opensource", "github", output='t', disable_web_page_preview=True)
def github_link():
    return "https://github.com/SandaruKasa/SKTG/tree/dev"


@base.command("shrug", output='t')
def shrug():
    return r"¯\_(ツ)_/¯"


@base.command("uptime", output='t')
def uptime(_message: telegram.Message, context: telegram.ext.CallbackContext):
    try:
        result = str(sktg.config.get_uptime(context.bot.id))
        # stripping microseconds
        return result.split('.')[0]
    except KeyError:
        # todo: log an error or something
        return "Startup time wasn't set up for this bot"
