# What is this?
This is the source code of my Telegram bot.

# Running
## You'll need:
0. Git, lol
1. Rust (1.59 or later) or Docker (preferably with docker-compose)
2. A Telegram Bot API token

## Preparations:
0. Clone the repo, obviously.
1. Save your token into the `token.txt` file in the root of the repo.
2. Create a database file
```shell
touch sktg.sqlite3
```
3. On Linux you will need to have `libssl-dev` and `pkg-config`
installed to build this without Docker.
If you're running Ubuntu,
```shell
sudo apt install libssl-dev pkg-config -y
```
4. You might want to make yourself an admin of the bot.
To do that, put your Telegram id to the
`admins.txt` file in the root of the repo.

## Building and running:
### Docker:
0. For the ease of development, you can copy the 
[`docker-compose.debug.yml`](docker-compose.debug.yml) file
to `docker-compose.override.yml`:
it increases the verbosity of logging
and disables auto-restarts of the docker-compose service.
1. Just run
```shell
docker-compose up
```

### No Docker:
1.
```shell
cargo run
```
That's it.

## P.S.
* You can change logging verbosity by passing a `RUST_LOG` env variable.
Like this if you're on Linux:
```shell
RUST_LOG=DEBUG python3 -m sktg
```
* You can change the path to the sqlite database file
by passing a `DATABASE_FILE` env variable.
* You can change the path to the file with your token
by passing a `BOT_TOKEN_FILE` env variable.
* Or you can just directly pass the token via a `BOT_TOKEN` env variable.

# Contributing
Just open a pull request or an issue!
I'll be grateful.


# Other stuff to look at
* `python` branch: the same bot but in Python.
* `python-old` branch: my old Telegram bots, written in Python a long time ago (not too proud of that code).
* `java` branch: an abandoned attempt to rewrite my old bots into Java.
