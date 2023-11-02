import random
import re

from ..telegram import *

ROUTER = Router(name="dice")

MIN_N = 1
MAX_N = 100_000
MIN_D = 1
MAX_D = 1_000_000_000

random.seed()


@ROUTER.message(filters.Command(re.compile("(\d*)d(\d+)")))
async def dice(message: types.Message, command: filters.command.CommandObject):
    n, d = command.regexp_match.groups()
    n = int(n or "1")
    d = int(d)
    if n < MIN_N:
        return await message.reply(
            gettext("The number of dice is too small. Minimum is {}.").format(MIN_N)
        )
    if n > MAX_N:
        return await message.reply(
            gettext("The number of dice is too big. Maximum is {}").format(MAX_N)
        )
    if d < MIN_D:
        return await message.reply(
            gettext("The number of sides is too small. Minimum is {}").format(MIN_D)
        )
    if d > MAX_D:
        return await message.reply(
            gettext("The number of sides is too big. Maximum is {}").format(MAX_D)
        )
    return await message.reply(text=str(sum(random.randint(1, d) for _ in range(n))))
