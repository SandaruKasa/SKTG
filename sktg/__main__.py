"""A file that starts the bots.
Created to allow running the bots with ``python3 -m sktg``.
"""
import logging
import os
from datetime import datetime

import aiogram

from . import config, features, persistance, scheduler, telegram

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=config.datetime_fmt,
)


async def message_admins(text: str):
    for admin in persistance.BotAdmin.select():
        try:
            await telegram.bot.send_message(chat_id=admin.user_id, text=text)
        except Exception as e:
            logging.error(f"Error sending {text!r} to admin {admin.user_id}: {e}")


async def on_startup(dp: aiogram.dispatcher):
    await telegram.register_commands()
    await message_admins("Hello!")
    config.startup_time = datetime.now()


async def on_shutdown(dp: aiogram.dispatcher):
    logging.info("Stopping...")
    await message_admins("Goodbye!")


logging.info("Starting...")
persistance.init()
scheduler.start()
aiogram.executor.start_polling(
    dispatcher=telegram.dp,
    on_startup=on_startup,
    on_shutdown=on_shutdown,
)
