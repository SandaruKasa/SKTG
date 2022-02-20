# todo: add comments to the module

import telegram.ext

from sktg import config, features, utils

updaters: list[telegram.ext.Updater] = []


def create_bot(
        name: str,
        *blueprints: utils.Blueprint,
        add_base_features=True,
        add_debug_features=False,
) -> telegram.ext.Updater:
    blueprint = utils.Blueprint(name)
    blueprint.add_blueprints(*blueprints)
    if add_base_features:
        blueprint.add_blueprints(features.base)
    if add_debug_features:
        blueprint.add_blueprints(features.debugger)
    updater = telegram.ext.Updater(config.get_token(name))
    blueprint.apply(updater.dispatcher)
    updaters.append(updater)
    return updater
