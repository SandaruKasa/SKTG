# What is this?
This is the source code of my Telegram bot.

# Running
## You'll need:
0. Git, lol
1. Rust (1.58 or later)
2. A Telegram Bot API token

## Preparations:
0. Clone the repo, obviously.
1. Save your token into the `token.txt` file in the root of the repo.
2. On Linux you will need to have `libssl-dev` and `pkg-config` installed to build this.
If you're running Ubuntu,
```shell
sudo apt install libssl-dev pkg-config -y
```
## Building and running:
1.
```shell
cargo run
```
That's it.

## P.S.
* This is not a rust/cargo guide, so you might want to look up things like
```shell
cargo run --release
```
```shell
cargo build
```
```shell
cargo check
```
* You can change logging verbosity by passing a `RUST_LOG` env variable.
Like this if you're on Linux:
```shell
RUST_LOG=DEBUG cargo run
```
* You can change the path to the file with your token
by passing a `BOT_TOKEN_FILE` env variable.
* Or you can just directly pass the token via
either a `TELOXIDE_TOKEN` or a `BOT_TOKEN` env variable.

# Contributing
Just open a pull request or an issue!

# Other stuff to look at
* `python` branch: the same bot but in Python.
* `python-old` branch: my old Telegram bots, written in Python a long time ago (not too proud of that code).
* `java` branch: an abandoned attempt to rewrite my old bots into Java.
