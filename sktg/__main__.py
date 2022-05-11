"""A file that starts the bots.
Created to allow running the bots with ``python3 -m sktg``.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

import telegram.ext

from . import config, features, persistance, tg_utils

logging.basicConfig(
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path("logs") / f"{datetime.utcnow().strftime(config.datetime_fmt)}.log",
            encoding="UTF-8",
            mode="w",
        ),
    ],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=config.datetime_fmt,
)

updater = telegram.ext.Updater(config.token)
logger = logging.getLogger(updater.bot.username)


logger.info("Starting...")
persistance.init()
tg_utils.Blueprint(
    "junior",
    features.base,
    features.shrooms,
    features.inspirobot,
).apply(updater.dispatcher)
updater.start_polling()
config.startup_time = datetime.now()
logger.info("Started")
updater.idle()
logger.info("Stopped")
