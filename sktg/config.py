"""Parsing configs and storing tokens/uptimes
"""

import datetime
import os
from pathlib import Path
import pathlib

datetime_fmt = r"%Y-%m-%dT%H-%M-%S"

temp_dir = Path("temp")
temp_dir.mkdir(parents=True, exist_ok=True)


def _get_temp_file_name() -> str:
    return datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")


def get_temp_file_path() -> pathlib.Path:
    return temp_dir / _get_temp_file_name()


config_dir = Path("config")
assert config_dir.is_dir(), "Config directory doesn't exist"


token = os.getenv("TOKEN")
if token is None:
    with open(config_dir / "token.txt") as f:
        token = f.read().strip()


startup_time: None | datetime.datetime = None


def get_uptime() -> datetime.timedelta | None:
    if startup_time is not None:
        return datetime.datetime.now() - startup_time
    else:
        return None
