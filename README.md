# THIS THING IS OUTDATED AS HELL, I'M GOING TO REWRITE IT AFTER I FINISH REWRITING THE CODE ITSELF

# 0. Bot-unspecific files

0.0. /tokens.py is a file that contains IDs of groups and chats and tokens for VK and Telegram access.
The file is not present here for obvious reasons.

0.1. /tools.py contains two things:
0.1.1. safeguard, a generator of decorators for a wrapper that can retry
running a function in case of it raising an exception for as many times as you want
and even provide a bit of a traceback if it exceeds the number of allowed retries.
0.1.2. Logger, a custom class responsible for logging in two ways: both on screen via the current thread
and (if desired) to Telegram via a separate thread.

0.2. /links.py is a storage for links such as Telegram Bot API address, VK API address,
and http/https proxies for connecting Telegram from Russia.

0.3. /startup.bat starts both bots


# 1. ImperialDrone

1.0. This Telegram bot reposts posts from a VK community to a Telegram chat.
It handles both new and old posts in their separate chronological orders.

1.1. /ImpDro.py is the main file with the working directory /impdro/ (/impdro/ not present due to unnecessity)

# 2. BetaLupi

2.0. My personal bot with various features

2.1. /BetaLupi.py is the main file with the working directory /betalupi/

2.2. /betalupi/bot picture/Lupus.png astrological symbol of Lupi constellation, /betalupi/bot picture/β lupi.png the profile picture for the bot
