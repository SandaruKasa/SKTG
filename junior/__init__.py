import asyncio
import logging
import os
from pathlib import Path

from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

import sktg

from . import features, scheduler

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=r"%Y-%m-%dT%H-%M-%S",
)


def main():
    scheduler.start()
    sktg.run_bot("junior", *features.ROUTERS)
