from __future__ import annotations

from typing import Callable, TypeVar

import telegram.ext

R = TypeVar('R')
_Callback = Callable[[telegram.Update, telegram.ext.CallbackContext], R]


class Blueprint:
    def __init__(self, name: str):
        self.name: str = name
        self.groups: dict[str, list[telegram.ext.Handler]] = {}
        self.blueprints: list['Blueprint'] = []
        self.commands: list[tuple[str, str]] = []

    def add_blueprints(self, *blueprints: 'Blueprint'):
        self.blueprints.extend(blueprints)

    def apply(self, dispatcher: telegram.ext.Dispatcher):
        group_ids: dict[str, int] = {}
        self._apply(dispatcher, group_ids)
        if self.commands:
            # todo: l10n
            # todo: scopes
            dispatcher.bot.set_my_commands(self.commands)

    def _apply(self, dispatcher: telegram.ext.Dispatcher, group_ids: dict[str, int]):
        for group_name, handlers in self.groups.items():
            group_id: int = group_ids.setdefault(group_name, len(group_ids))
            for handler in handlers:
                dispatcher.add_handler(handler, group_id)
        for blueprint in self.blueprints:
            blueprint._apply(dispatcher, group_ids)

    def add_handler(self, handler: telegram.ext.Handler, group: str | None = None):
        if group is None:
            group = self.name
        self.groups.setdefault(group, []).append(handler)

    # todo: pass filter as an explicit argument
    def command(self, name: str, *aliases: str, description: str | None = None, group: str = "commands", **kwargs):
        def decorator(callback: _Callback) -> _Callback:
            self.add_handler(
                handler=telegram.ext.CommandHandler(
                    command=[name, *aliases],
                    callback=callback,
                    **kwargs
                ),
                group=group
            )
            return callback

        if description is not None:
            self.commands.append((name, description))

        return decorator

    # todo: regexp analogous to command
