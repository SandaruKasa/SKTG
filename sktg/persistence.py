import logging
import os
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import peewee
from peewee import DateTimeField, IntegerField, PrimaryKeyField, TextField

from . import config

logger = logging.getLogger(__name__)


database = peewee.SqliteDatabase(
    config.get_database_path(),
    pragmas={"foreign_keys": 1},
)


class BaseModel(peewee.Model):
    class Meta:
        database = database


models = []


def create_table(model: BaseModel):
    models.append(model)
    return model


def init():
    logger.debug("Initializing the database...")
    with database:
        logger.debug(f"Creating tables for {len(models)} models...")
        database.create_tables(models)
    logger.info("Database initialized")
    init_admins()


@create_table
class BotAdmin(BaseModel):
    user_id = IntegerField(unique=True, index=True)

    @staticmethod
    def add(user_id: int) -> bool:
        return BotAdmin.get_or_create(user_id=user_id)[1]


def init_admins():
    path = Path(os.getenv("BOT_ADMINS_FILE", "admins.txt"))
    if path.exists():
        logger.info(f"Found {path}, initializing admins...")
        with database.atomic():
            admins = []
            with open(path) as f:
                for line in f:
                    if line := line.strip():
                        admins.append(int(line))
            logger.info(f"Found {len(admins)} entires in {path}")
            added = list(map(BotAdmin.add, admins)).count(True)
            logger.info(f"Added {added} new admins to the database")
        logger.info("Admins initialized")
    else:
        logger.info(f"{path} doesn't exist, so not initializing admins")
