import random
import re

from ..telegram import *

MIN_N = 1
MAX_N = 100_000
MIN_D = 2
MAX_D = 100_000

random.seed()


@dp.message_handler(filters.RegexpCommandsFilter(["(\d*)d(\d+)"]))
async def dice(message: types.Message, regexp_command: re.Match):
    n, d = regexp_command.groups()
    n = int(n or "1")
    d = int(d)
    if n < MIN_N:
        return await message.reply(f"Number of dice is too small. Minimum is {MIN_N}.")
    if n > MAX_N:
        return await message.reply(f"Number of dice is too big. Maximum is {MAX_N}.")
    if d < MIN_D:
        return await message.reply(f"Number of sides is too small. Minimum is {MIN_D}.")
    if d > MAX_D:
        return await message.reply(f"Number of sides is too big. Maximum is {MAX_D}.")
    return await message.reply(sum(random.randint(1, d) for _ in range(n)))
