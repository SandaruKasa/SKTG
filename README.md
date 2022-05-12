# What is this?
This is the source code of my Telegram bot.

# Running
## You'll need:
0. Git, lol
1. Python (3.10 or later) or Docker (preferebaly with docker-compose)
2. A Telegram Bot API token

## Preparations:
0. Clone the repo, obviously.
1. Save your token into the `config/token.txt` file
([here](config/token.example.txt)'s an example)
2. You might want to put you Telegram ID (your, not your bot's)
into the `config/admins_override.txt` file,
because some of the bot commands are only available for admins.
You can even put multiple IDs, if you want to.
(Note that you have to put the ID, and not the @username.
To find out your ID, you can use a `/tme` command
of [this bot](https://t.me/sliva0bot), for example.)

## Running:
### Docker:
0. For the ease of development, you can copy the 
[`docker-compose.debug.yml`](docker-compose.debug.yml) file
to `docker-compose.override.yml`:
it makes `docker-compose` mount the source code folder
into the container, so that you don't have to
rebuild the image every time you make a change,
and it also increases the verbosity of logging.
1. Run 
```shell
docker-compose up
```

That's it. This is not a Docker guide,
so you might want to look up things like
```shell
docker-compose up --build
```
```shell
docker-compose up --detach
```
```shell
docker-compose down
```
```shell
docker-compose logs
```
if you're not familiar with Docker yet.

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
python3 -m sktg
```

# Contributing
Just open a pull request or an issue!
<!-- todo: a list of things I can use some help with -->
