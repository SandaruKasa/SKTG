"""A file that starts the bots.
Created to allow running the bots with ``python3 -m sktg``.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

import aiogram

from . import config, features, persistance, scheduler, telegram

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


async def on_startup(dp: aiogram.dispatcher):
    logging.info("Starting...")
    persistance.init()
    scheduler.start()
    await telegram.register_commands()
    config.startup_time = datetime.now()


async def on_shutdown(dp: aiogram.dispatcher):
    logging.info("Stopping...")


aiogram.executor.start_polling(
    dispatcher=telegram.dp,
    on_startup=on_startup,
    on_shutdown=on_shutdown,
)
