import telegram.ext

from sktg import config, features, utils

bots: list[telegram.ext.Updater] = []


def create_bot(name: str, *blueprints: utils.Blueprint) -> telegram.ext.Updater:
    blueprint = utils.Blueprint(name)
    blueprint.add_blueprints(*blueprints)
    updater = telegram.ext.Updater(config.get_token(name))
    blueprint.apply(updater.dispatcher)
    bots.append(updater)
    return updater
