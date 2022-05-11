import datetime
import logging
import pathlib
from dataclasses import dataclass
from typing import Callable, Iterable

import peewee
from peewee import IntegerField, TextField

from . import config

logger = logging.getLogger(__name__)


database = peewee.SqliteDatabase(config.config_dir / "database.sqlite3")


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


def migration(priroity: int = 0):
    def decorator(task: Callable[[], None]):
        migrations.append(Migration(task=task, priority=priroity))

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


@create_table
class BotAdmin(BaseModel):
    user_id = IntegerField(unique=True, index=True)

    @staticmethod
    def add(user_id: int) -> bool:
        return BotAdmin.get_or_create(user_id=user_id)[1]


def add_admins_from_txt(file: pathlib.Path):
    assert file.is_file()
    admins = []
    with open(file) as f:
        for line in f:
            line = line.strip()
            if line:
                admins.append(int(line))
    with database.atomic():
        result = list(map(BotAdmin.add, admins))
    logger.info(
        f"Found {len(result)} admins in {file}, "
        f"added {result.count(True)} new to the databse"
    )
    file.rename(file.with_suffix(f".migrated{file.suffix}"))


@migration(priroity=100)
def admins_override():
    override = config.config_dir / "admins_override.txt"
    backup = config.config_dir / "admins_backup.txt"

    if override.exists():
        with open(backup, "a") as f:
            f.write(datetime.datetime.utcnow().strftime(config.datetime_fmt))
            f.write("\n")
            for bot_admin in BotAdmin.select():
                f.write(f"{bot_admin.user_id}\n")
                bot_admin.delete_instance()
            f.write("\n")
        return add_admins_from_txt(override)
