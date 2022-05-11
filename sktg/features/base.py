"""Basic functionality I would like all the bots to have.
Added to a bot by the ``create_bot`` function of the module by default.
"""

import sktg.uptime
import telegram.ext
from sktg.utils import Blueprint

base = Blueprint("base")


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
