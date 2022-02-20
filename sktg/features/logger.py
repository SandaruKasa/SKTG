import datetime
import json
import logging
import pathlib

import telegram.ext

from sktg.utils import Blueprint

logger = Blueprint("logger")

logging_dir = pathlib.Path("logs").resolve()
logging_dir.mkdir(exist_ok=True)

logging.basicConfig(
    filename=logging_dir / f"{datetime.datetime.now().isoformat()}.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def format_update(update: telegram.Update | str) -> str:
    if isinstance(update, telegram.Update):
        return json.dumps(update.to_dict(), indent=4, ensure_ascii=False)
    else:
        return str(update)


def log_update(update: telegram.Update | str, context: telegram.ext.CallbackContext):
    if isinstance(update, telegram.Update):
        update = json.dumps(update.to_dict(), indent=4, ensure_ascii=False)
    logging.getLogger(f"{context.bot.username}: UPDATE").info("\n%s", update)


class LoggingHandler(telegram.ext.Handler):
    def __init__(self):
        super().__init__(callback=log_update)

    # Currently, set to log all updates except new/edited messages/posts.
    # It's hard to find a good balance between thorough logging and user privacy.
    def check_update(self, update) -> bool:
        if isinstance(update, telegram.Update):
            return not (update.message or update.edited_message or update.channel_post or update.edited_channel_post)
        else:
            return True


logger.add_handler(LoggingHandler())
