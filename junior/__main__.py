import logging
from pathlib import Path

from sktg import persistence, scheduler, telegram

if __package__:
    from . import features
else:
    import features

logging.info("Starting...")
persistence.init()
scheduler.start()
telegram.setup_i18n(locales_dir=Path(__file__).parent / "locales")
telegram.start_polling()
