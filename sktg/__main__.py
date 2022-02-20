from sktg import *

create_bot(
    "junior",
    # todo: features
)

for bot in bots:
    bot.start_polling()

if bots:
    bots[0].idle()
    for bot in bots[1:]:
        bot.stop()
