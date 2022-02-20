import inspect
from typing import TypeVar

import telegram.ext

F = TypeVar('F')


class Blueprint:
    def __init__(self, name: str, *blueprints: 'Blueprint'):
        self.name: str = name
        self._groups: dict[str, list[telegram.ext.Handler]] = {}
        self._blueprints: list['Blueprint'] = list(blueprints)
        self._commands: list[tuple[str, str]] = []

    def add_blueprints(self, *blueprints: 'Blueprint'):
        self._blueprints.extend(blueprints)

    def apply(self, dispatcher: telegram.ext.Dispatcher):
        group_ids: dict[str, int] = {}
        self._apply(dispatcher, group_ids)
        if self._commands:
            # todo: l10n
            # todo: scopes
            dispatcher.bot.set_my_commands(self._commands)

    def _apply(self, dispatcher: telegram.ext.Dispatcher, group_ids: dict[str, int]):
        for group_name, handlers in self._groups.items():
            group_id: int = group_ids.setdefault(group_name, len(group_ids))
            for handler in handlers:
                dispatcher.add_handler(handler, group_id)
        for blueprint in self._blueprints:
            blueprint._apply(dispatcher, group_ids)

    def add_handler(self, handler: telegram.ext.Handler, group: str | None = None):
        if group is None:
            group = self.name
        self._groups.setdefault(group, []).append(handler)

    # todo: return type of the function
    def command(
            self,
            name: str,
            *aliases: str,
            filters: telegram.ext.BaseFilter | None = None,
            output: str | None = None,
            description: str | None = None,
            group: str = "commands",
            **reply_kwargs,
    ):
        def decorator(function: F) -> F:

            arity = len(inspect.signature(function).parameters)
            assert arity <= 2, f"{function} provided as a callback for command {name} of Blueprint {self.name} " \
                               f"takes {arity} arguments while 0 to 2 are expected"

            match output:
                case None:
                    reply_function = None
                case "text" | "t":
                    reply_function = telegram.Message.reply_text
                case "sticker" | "s":
                    reply_function = telegram.Message.reply_sticker
                case _:
                    raise ValueError(
                        f"{function} provided as a callback for command {name} of Blueprint {self.name} "
                        f"wants to have {output} as output, which is not a recognized option"
                    )

            def callback(update: telegram.Update, context: telegram.ext.CallbackContext):
                message = update.effective_message
                args = []
                if arity >= 1:
                    args.append(message)
                if arity >= 2:
                    args.append(context)
                result = function(*args)
                if reply_function is not None:
                    reply_function(
                        message,
                        result,
                        **{"quote": True, **reply_kwargs}
                    )

            self.add_handler(
                handler=telegram.ext.CommandHandler(
                    command=[name, *aliases],
                    callback=callback,
                    filters=filters,
                ),
                group=group,
            )
            return function

        if description is not None:
            self._commands.append((name, description))

        return decorator

    # todo: regexp analogous to command
