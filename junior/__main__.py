import logging

from sktg import persistence, scheduler, telegram

if __package__:
    from . import features
else:
    import features

logging.info("Starting...")
persistence.init()
scheduler.start()
telegram.start_polling()
