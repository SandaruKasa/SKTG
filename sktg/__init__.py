import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

from . import dispatching, persistence, telegram

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=r"%Y-%m-%dT%H-%M-%S",
)


def run_bot(name: str, *features: telegram.Router):
    logging.info("Starting...")
    persistence.init()
    dispatching.init_i18n(domain=name)
    dispatching.dispatcher.include_routers(*features)
    asyncio.run(
        main=dispatching.start_polling(
            bot=telegram.Bot(
                token=config.get_token(),
            )
        )
    )
