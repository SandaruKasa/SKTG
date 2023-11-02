import asyncio
import logging
import os
from pathlib import Path

from . import features, persistence, scheduler, telegram

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=r"%Y-%m-%dT%H-%M-%S",
)


def main():
    logging.info("Starting...")
    persistence.init()
    scheduler.start()
    # TODO: read env for locale path
    telegram.setup_i18n(locales_dir=Path(__file__).parent / "locales")
    telegram.dispatcher.include_routers(*features.ROUTERS)
    asyncio.run(telegram.start_polling())
