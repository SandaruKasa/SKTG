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


@migration(priroity=100)
def admins_override():
    override_file = config.config_dir / "admins_override.txt"
    backup_file = config.config_dir / "admins_backup.txt"

    if not override_file.exists():
        return

    logger.info(f"Found {override_file}, applying...")

    with database.atomic():
        if admins := BotAdmin.select():
            logger.info("Backing up previous admins...")
            backed_up = 0
            with open(backup_file, "a") as f:
                f.write(datetime.datetime.utcnow().strftime(config.datetime_fmt))
                f.write("\n")
                for bot_admin in admins:
                    f.write(f"{bot_admin.user_id}\n")
                    bot_admin.delete_instance()
                    backed_up += 1
                f.write("\n")
            logger.info(f"Backed up {backed_up} previously set admins")

        admins = []
        with open(override_file) as f:
            for line in f:
                if line := line.strip():
                    admins.append(int(line))
        logger.info(f"Found {len(admins)} entires in {override_file}")

        added = list(map(BotAdmin.add, admins)).count(True)
        logger.info(f"Added {added} new admins to the databse")
        override_file.rename(
            override_file.with_suffix(f".migrated{override_file.suffix}")
        )
