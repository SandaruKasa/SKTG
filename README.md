# What's this?

This branch is an archived version of the source code for my Telegram bots that I created in the summer of 2020.

I'm not particularly proud of this code. It was essentially my first experience of writing code that actually does
something and not just solves simple MOOC python tasks, so no wonder I didn't create a masterpiece on my first try.

# Where should I go?

Probably to the `dev` branch. Or the `main`/`master` (whatever it is).

Alternatively, you can take a look at the `java` branch to see my unfinished  (and abandoned) attempt to rewrite the
code from this branch into Java.

# Boring history

This started mostly as an HTML scraper to repost pictures from VK to Telegram. Back then Telegram was blocked in Russia
and I didn't manage to figure out how to use proxy in [cool BotAPI libs](https://python-telegram-bot.org/), so I wrote
everything by hand using only the `requests` lib.

The small scraping tool quickly became my main hobby for that summer and evolved into a couple of Telegram bots that
used lots of different stuff for their features (ffmpeg, Pillow, VKApi and whatnot).

Then came the autumn, I learned about Java, liked its strict typing and checked exceptions, and decided to rewrite
everything in it. After all, manipulating untyped Python dictionaries over several thousands lines of code was an
unnecessarily convoluted task (at least with my code organization abilities from back then). But soon I got too busy and
had to abandon this project. ¯\_(ツ)_/¯
