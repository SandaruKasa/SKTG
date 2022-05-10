"""A file that starts the bots.
Created to allow running the bots with ``python3 -m sktg``.
"""
from sktg import *

create_bot(
    "junior",
    features.shrooms,
    features.inspirobot,
)

for updater in updaters:
    updater.start_polling()
    config.set_startup_time(updater.bot.id)

if updaters:
    updaters[0].idle()  # todo: custom idler with logging
    for updater in updaters[1:]:
        updater.stop()
