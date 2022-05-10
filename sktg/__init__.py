import datetime
import logging
import os

from sktg import config, features, utils

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
