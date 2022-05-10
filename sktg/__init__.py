import datetime
import logging
import os

from sktg import features, uptime, utils

import telegram
import telegram.ext

datetime_fmt = r"%Y-%m-%dT%H-%M-%S"

logging.basicConfig(
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            f"./logs/{datetime.datetime.utcnow().strftime(datetime_fmt)}.log",
            encoding="UTF-8",
            mode="w",
        ),
    ],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=datetime_fmt,
)

token = os.getenv("TOKEN")
if token is None:
    with open("token.txt") as f:
        token = f.read().strip()

updater = telegram.ext.Updater(token)
del token
logger = logging.getLogger(updater.bot.username)

utils.Blueprint("junior", features.base, features.shrooms, features.inspirobot).apply(
    updater.dispatcher
)
