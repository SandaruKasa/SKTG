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
    result: str
    try:
        result = str(sktg.config.get_uptime(context.bot.id))  # todo: pretty format
    except KeyError:
        result = "Startup time wasn't set up for this bot"  # todo: log an error or something
    return result
