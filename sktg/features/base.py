"""Basic functionality I would like all the bots to have.
Added to a bot by the ``create_bot`` function of the module by default.
"""

from .. import config, tg_utils

base = tg_utils.Blueprint("base")


@base.command(
    "source", "opensource", "github", output="t", disable_web_page_preview=True
)
def github_link():
    return "https://github.com/SandaruKasa/SKTG/tree/dev"


@base.command("shrug", output="t")
def shrug():
    return r"¯\_(ツ)_/¯"


@base.command("uptime", output="t", filters=tg_utils.BOT_ADMIN_FILTER)
def uptime():
    result = config.get_uptime()
    if result is None:
        return "Unknown"
    else:
        # stripping microseconds
        return str(result).split(".")[0]
