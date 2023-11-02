"""Parsing configs and storing tokens/uptimes
"""

import datetime
import os
from pathlib import Path

TEMP_DIR = Path(os.getenv("TMP_DIR", "tmp"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def _get_temp_file_name() -> str:
    return datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")


def get_temp_file_path() -> Path:
    return TEMP_DIR / _get_temp_file_name()


def get_database_path() -> Path:
    return Path(os.getenv("DATABASE_FILE", "sktg.sqlite3"))


def get_locale_path() -> str | Path:
    if path := os.getenv("LOCALE_PATH"):
        return path
    path = Path("locale")
    return path if path.exists() else "/usr/share/locale/"


def get_token() -> str:
    token = os.getenv("BOT_TOKEN")
    if token is None:
        with open(os.getenv("BOT_TOKEN_FILE", "token.txt")) as f:
            token = f.read().strip()
    return token
