import telegram.ext

import sktg.config
from sktg.utils import Blueprint
from .logger import logger

base = Blueprint("base", logger)


@base.command("source", "opensource", "github")
def github_link(update: telegram.Update, context: telegram.ext.CallbackContext):
    update.message.reply_text(
        "https://github.com/SandaruKasa/SKTG/tree/dev",
        disable_web_page_preview=True,
        quote=True,
    )


@base.command("shrug")
def shrug(update: telegram.Update, context: telegram.ext.CallbackContext):
    update.message.reply_text(r"¯\_(ツ)_/¯")


@base.command("uptime")
def uptime(update: telegram.Update, context: telegram.ext.CallbackContext):
    text: str
    try:
        text = str(sktg.config.get_uptime(context.bot.id))  # todo: pretty format
    except KeyError:
        text = "Startup time wasn't set up for this bot"  # todo: log an error or somethign
    update.message.reply_text(text=text)
