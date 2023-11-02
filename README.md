<!-- FIXME: outdated -->

# This README is outdated, sorry

# What is this?
This is the source code of my Telegram bot.

# Running
## You'll need:
0. Git, lol
1. Python (3.10 or later) or Docker (preferably with docker-compose)
2. A Telegram Bot API token

## Preparations:
0. Clone the repo, obviously.
1. Save your token into the `token.txt` file in the root of the repo.
2. You might want to make yourself an admin of the bot.
To do that, put your Telegram id to the
`admins.txt` file in the root of the repo.

## Running:
### Docker:
0. For the ease of development, you can copy the 
[`docker-compose.debug.yml`](docker-compose.debug.yml) file
to `docker-compose.override.yml`:
it increases the verbosity of logging
and disables auto-restarts of the service.
1. Just run
```shell
docker-compose up
```

### No Docker:
0. Set up a `venv`:
```shell
python3.10 -m venv venv
source venv/bin/activate
```
1. Install the dependencies:
```shell
pip install -r requirements.txt
```
2. Run the code:
```shell
python3 -m junior
```

## P.S.
* You can change logging verbosity by passing a `LOGLEVEL` env variable.
Like this if you're on Linux:
```shell
LOGLEVEL=DEBUG python3 -m junior
```
* You can change the path to the sqlite database file
by passing a `DATABASE_FILE` env variable.
* You can change the path to the file with bot admin ids
by passing a `BOT_ADMINS_FILE` env variable.
* You can change the path to the file with your token
by passing a `BOT_TOKEN_FILE` env variable.
* Or you can just directly pass the token via a `BOT_TOKEN` env variable.
* And you can change the path to bot's tmp directory
by passing a `TMP_DIR` env variable.

# Contributing
Just open a pull request or an issue!
I'll be grateful.

# Other stuff to look at
* `rust` branch: an abandoned attempt to rewrite the same bot in Rust.
* `python-old` branch: my old Telegram bots, written in Python a long time ago (not too proud of that code).
* `java` branch: an abandoned attempt to rewrite my old bots into Java.
