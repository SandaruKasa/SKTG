import datetime
import json
import pathlib

config_dir = pathlib.Path("config").resolve()
assert config_dir.is_dir()

_token_file = config_dir / "tokens.json"
_tokens: dict[str, str] = json.load(open(_token_file))

_startup_time: dict[int, datetime.datetime] = {}


def get_token(bot_name: str) -> str:
    return _tokens[bot_name]


def set_startup_time(bot_id: int):
    _startup_time[bot_id] = datetime.datetime.now()


def get_uptime(bot_id: int) -> datetime.timedelta:
    return datetime.datetime.now() - _startup_time[bot_id]
