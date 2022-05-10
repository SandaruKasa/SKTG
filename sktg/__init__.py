"""The module with my Telegram bots, what else can I say?
"""

import datetime
import logging
import os

datetime_fmt = r"%Y-%m-%dT%H-%M-%S"

logging.basicConfig(
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            f"./logs/{datetime.datetime.utcnow().strftime(datetime_fmt)}.log",
            encoding="UTF-8",
            mode="w",
        ),
    ],
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s",
    datefmt=datetime_fmt
)


import telegram.ext

from sktg import config, features, utils

updaters: list[telegram.ext.Updater] = []


def create_bot(
        name: str,
        *blueprints: utils.Blueprint,
        add_base_features: bool = True,
) -> telegram.ext.Updater:
    """Set up a bot

    Creates a default ``Updater`` for a bot, populates its ``Dispatcher`` with ``Handlers`` from the provided ``Blueprints``.
    Puts the created ``Updater`` into the ``updaters`` list and also returns it (the updater, not the list).

    Args:
        name (str): local name of the bot to set up, must be a vallid input for ``sktg.config.get_token``
        *blueprints: Blueprints to add to the bot
        add_base_features (bool, optional): flag indicating whether the ``sktg.features.base`` blueprint should be added. Defaults to True.

    Returns:
        telegram.ext.Updater: the ``Updater`` created for the bot
    """
    bot_blueprint = utils.Blueprint(name)
    bot_blueprint.add_child_blueprints(*blueprints)
    if add_base_features:
        bot_blueprint.add_child_blueprints(features.base)
    updater = telegram.ext.Updater(config.get_token(name))
    bot_blueprint.apply(updater.dispatcher)
    updaters.append(updater)
    return updater
