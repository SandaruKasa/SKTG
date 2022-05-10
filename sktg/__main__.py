"""A file that starts the bots.
Created to allow running the bots with ``python3 -m sktg``.
"""
from sktg import *

logger.info("Starting...")
updater.start_polling()
uptime.set_startup_time(updater.bot.id)
logger.info("Started")
updater.idle()
logger.info("Stopped")
