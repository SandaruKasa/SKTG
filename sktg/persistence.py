import datetime
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
    config.database_file,
    pragmas={"foreign_keys": 1},
)


class BaseModel(peewee.Model):
    class Meta:
        database = database


models = []


def create_table(model: BaseModel):
    models.append(model)
    return model


@dataclass
class Migration:
    task: Callable[[], None]
    priority: int = 0


migrations: list[Migration] = []


# TODO: come up with a better way
def migration(priority: int = 0):
    def decorator(task: Callable[[], None]):
        migrations.append(Migration(task=task, priority=priority))

    assert isinstance(priority, int), (
        "You should call migration()"
        if isinstance(priority, typing.Callable)
        else "priority should be an integer"
    )
    return decorator


def init():
    logger.debug("Initializing the database...")
    with database:
        logger.debug(f"Creating tables for {len(models)} models...")
        database.create_tables(models)

        migrations.sort(key=lambda m: m.priority)
        n = len(migrations)
        for (i, migration) in enumerate(migrations, start=1):
            logger.debug(f"Running migration {i}/{n}: {migration.task.__name__}")
            migration.task()
        logger.debug("Migrations applied")
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
