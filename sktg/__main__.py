"""A file that starts the bots.
Created to allow running the bots with ``python3 -m sktg``.
"""
from sktg import *

create_bot(
    "junior",
    features.shrooms,
    features.inspirobot,
)

logging.info("Starting...")

for updater in updaters:
    updater.start_polling()
    config.set_startup_time(updater.bot.id)

logging.info("Started")


def log_stopped(updater: telegram.ext.Updater):
    logging.getLogger(updater.bot.username).info("Stopped")


if updaters:
    updaters[0].idle()  # todo: custom idler with logging
    log_stopped(updaters[0])
    for updater in updaters[1:]:
        updater.stop()
        log_stopped(updater)
