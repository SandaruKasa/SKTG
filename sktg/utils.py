import inspect
import typing

import telegram
import telegram.ext

F = typing.TypeVar("F")
R = typing.TypeVar("R")
CommandCallback = typing.Callable[[telegram.Message, telegram.ext.CallbackContext], R]
Callback = typing.Callable[[telegram.Update, telegram.ext.CallbackContext], R]


def wrap_command_callback(command_callback: CommandCallback) -> Callback:
    def callback(update: telegram.Update, context: telegram.ext.CallbackContext):
        return command_callback(update.effective_message, context)

    return callback


class Blueprint:
    def __init__(self, name: str, *blueprints: "Blueprint"):
        self.name: str = name
        self._groups: dict[str, list[telegram.ext.Handler]] = {}
        self._children: list["Blueprint"] = list(blueprints)
        self._commands: list[tuple[str, str]] = []

    def add_child_blueprints(self, *blueprints: "Blueprint"):
        self._children.extend(blueprints)

    def apply(self, dispatcher: telegram.ext.Dispatcher):
        group_ids: dict[str, int] = {}
        applied_blueprints: set[str] = set()
        self._apply(dispatcher, group_ids, applied_blueprints)
        if commands := list(self._all_comands()):
            dispatcher.bot.set_my_commands(commands)

    def _all_comands(self):
        for child in self._children:
            yield from child._all_comands()
        for command in self._commands:
            yield command

    def _apply(
        self,
        dispatcher: telegram.ext.Dispatcher,
        group_ids: dict[str, int],
        applied_blueprints: set[str],
    ):
        for child in self._children:
            child._apply(dispatcher, group_ids, applied_blueprints)
        if self.name in applied_blueprints:
            raise Exception(
                f"Error applying blueprint {self.name}: circular dependencies"
            )
        applied_blueprints.add(self.name)
        for group_name, handlers in self._groups.items():
            group_id: int = group_ids.setdefault(group_name, len(group_ids))
            for handler in handlers:
                dispatcher.add_handler(handler, group_id)

    def add_handler(self, handler: telegram.ext.Handler, group: str | None = None):
        if group is None:
            group = self.name
        self._groups.setdefault(group, []).append(handler)

    # todo: rewrite and comment this convoluted hellscape
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
            assert arity <= 2, (
                f"{function} provided as a callback for command {name} of Blueprint {self.name} "
                f"takes {arity} arguments while 0 to 2 are expected"
            )

            # todo: chat actions
            match output:
                case None:
                    reply_function = None
                case "photo" | "p":
                    reply_function = telegram.Message.reply_photo
                case "text" | "t":
                    reply_function = telegram.Message.reply_text
                case "sticker" | "s":
                    reply_function = telegram.Message.reply_sticker
                case _:
                    raise ValueError(
                        f"{function} provided as a callback for command {name} of Blueprint {self.name} "
                        f"wants to have {output} as output, which is not a recognized option"
                    )

            def wrapper(
                message: telegram.Message, context: telegram.ext.CallbackContext
            ):
                args = []
                if arity >= 1:
                    args.append(message)
                if arity >= 2:
                    args.append(context)
                content = function(*args)
                if reply_function is None:
                    return content
                else:
                    return reply_function(
                        message, content, **{"quote": True, **reply_kwargs}
                    )

            self.add_handler(
                handler=telegram.ext.CommandHandler(
                    command=[name, *aliases],
                    callback=wrap_command_callback(wrapper),
                    filters=filters,
                ),
                group=group,
            )
            return wrapper

        if description is not None:
            self._commands.append((name, description))

        return decorator

    # todo: regexp analogous to command
