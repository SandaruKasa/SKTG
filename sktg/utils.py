import abc
import inspect
import json
import pathlib
import typing
from typing import TypeVar

import telegram.ext

F = TypeVar('F')
R = TypeVar('R')
CommandCallback = typing.Callable[
    [telegram.Message, telegram.ext.CallbackContext],
    R
]
Callback = typing.Callable[[telegram.Update, telegram.ext.CallbackContext], R]


def wrap_command_callback(command_callback: CommandCallback) -> Callback:
    def callback(update: telegram.Update, context: telegram.ext.CallbackContext):
        return command_callback(update.effective_message, context)

    return callback


class Blueprint:
    def __init__(self, name: str, *blueprints: 'Blueprint'):
        self.name: str = name
        self._groups: dict[str, list[telegram.ext.Handler]] = {}
        self._children: list['Blueprint'] = list(blueprints)
        self._commands: list[tuple[str, str]] = []

    def add_child_blueprints(self, *blueprints: 'Blueprint'):
        self._children.extend(blueprints)

    def apply(self, dispatcher: telegram.ext.Dispatcher):
        group_ids: dict[str, int] = {}
        applied_blueprints: set[str] = set()
        self._apply(dispatcher, group_ids, applied_blueprints)
        if self._commands:
            # todo: l10n
            # todo: scopes
            dispatcher.bot.set_my_commands(self._commands)

    def _apply(self, dispatcher: telegram.ext.Dispatcher, group_ids: dict[str, int], applied_blueprints: set[str]):
        for child in self._children:
            child._apply(dispatcher, group_ids, applied_blueprints)
        if self.name in applied_blueprints:
            raise Exception(
                f"Error applying blueprint {self.name}: circular dependencies")
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

            def wrapper(message: telegram.Message, context: telegram.ext.CallbackContext):
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
                        message,
                        content,
                        **{"quote": True, **reply_kwargs}
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


class WhitelistFilter(telegram.ext.MessageFilter):
    WL = typing.TypeVar('WL')

    def __init__(self, underlying_file: pathlib.Path, whitelist_default: WL):
        self._file = underlying_file.resolve()

        if self._file.exists():
            with open(self._file) as f:
                self._whitelist = self.deserialize(f.read())
        else:
            self._whitelist = whitelist_default

    @abc.abstractmethod
    def serialize(self, whitelist: WL) -> str:
        ...

    @abc.abstractmethod
    def deserialize(self, s: str) -> WL:
        ...

    def _flush(self):
        with open(self._file, 'w') as f:
            f.write(self.serialize(self._whitelist))


class UserWhitelistFilter(WhitelistFilter):
    def __init__(self, underlying_file: pathlib.Path):
        super().__init__(underlying_file, set())

    def filter(self, message: telegram.Message) -> bool:
        return message.from_user.id in self._whitelist

    def serialize(self, whitelist: set[int]) -> str:
        return '\n'.join(map(str, whitelist))

    def deserialize(self, s: str) -> set[int]:
        return set(map(int, s.strip().splitlines()))

    def remove(self, user_id: int) -> bool:
        if user_id in self._whitelist:
            self._whitelist.remove(user_id)
            self._flush()
            return True
        else:
            return False

    def add(self, user_id: int) -> bool:
        if user_id in self._whitelist:
            return False
        else:
            self._whitelist.add(user_id)
            self._flush()
            return True


class StickerWhitelistFilter(WhitelistFilter):
    def __init__(self, underlying_file: pathlib.Path):
        super().__init__(underlying_file, {"stickers": [], "sets": []})

    def serialize(self, whitelist: dict) -> str:
        return json.dumps(whitelist, indent=4)

    def deserialize(self, s: str) -> dict:
        return json.loads(s)

    @property
    def _stickers(self) -> list[str]:
        return self._whitelist["stickers"]

    @property
    def _sets(self) -> list[str]:
        return self._whitelist["sets"]

    def filter(self, message: telegram.Message) -> bool | None:
        if sticker := message.sticker:
            return sticker.file_unique_id in self._stickers or sticker.set_name in self._sets

    def add_stickers(self, *file_unique_ids: str) -> list[bool]:
        result = []
        for file_unique_id in file_unique_ids:
            if file_unique_id in self._stickers:
                result.append(False)
            else:
                self._stickers.append(file_unique_id)
                result.append(True)
        if any(result):
            self._flush()
        return result

    def add_set(self, set_name: str) -> bool:
        if set_name in self._sets:
            return False
        else:
            self._sets.append(set_name)
            self._flush()
            return True
