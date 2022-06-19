"""Parsing configs and storing tokens/uptimes
"""

import datetime
import os
from pathlib import Path

datetime_fmt = r"%Y-%m-%dT%H-%M-%S"

temp_dir = Path(os.getenv("TMP_DIR", "tmp"))
temp_dir.mkdir(parents=True, exist_ok=True)


def _get_temp_file_name() -> str:
    return datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")


def get_temp_file_path() -> Path:
    return temp_dir / _get_temp_file_name()


database_file = Path(os.getenv("DATABASE_FILE", "sktg.sqlite3"))
assert database_file.is_file()

token = os.getenv("BOT_TOKEN")
if token is None:
    with open(os.getenv("BOT_TOKEN_FILE", "token.txt")) as f:
        token = f.read().strip()


startup_time: None | datetime.datetime = None


def get_uptime() -> datetime.timedelta | None:
    if startup_time is not None:
        return datetime.datetime.now() - startup_time
    else:
        return None
