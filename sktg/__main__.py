"""A file that starts the bots.
Created to allow running the bots with ``python3 -m sktg``.
"""
import telegram
import telegram.ext

from sktg import *

updater = telegram.ext.Updater(config.get_token())
logger = logging.getLogger(updater.bot.username)

bot_blueprint = utils.Blueprint(
    "junior", features.base, features.shrooms, features.inspirobot
)
bot_blueprint.apply(updater.dispatcher)


logger.info("Starting...")
updater.start_polling()
config.set_startup_time(updater.bot.id)
logger.info("Started")
updater.idle()
logger.info("Stopped")
