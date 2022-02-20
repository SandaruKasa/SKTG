from sktg import *

create_bot(
    "junior",
    features.shrooms,
)

for updater in updaters:
    updater.start_polling()
    config.set_startup_time(updater.bot.id)

if updaters:
    updaters[0].idle()  # todo: custom idler with logging
    for updater in updaters[1:]:
        updater.stop()
