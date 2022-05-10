import abc
import json
import pathlib
import typing

import telegram
import telegram.ext

persistance_dir = pathlib.Path("config")

class WhitelistFilter(telegram.ext.MessageFilter):
    WL = typing.TypeVar("WL")

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
        with open(self._file, "w") as f:
            f.write(self.serialize(self._whitelist))


class UserWhitelistFilter(WhitelistFilter):
    def __init__(self, underlying_file: pathlib.Path):
        super().__init__(underlying_file, set())

    def filter(self, message: telegram.Message) -> bool:
        return message.from_user.id in self._whitelist

    def serialize(self, whitelist: set[int]) -> str:
        return "\n".join(map(str, whitelist))

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
            return (
                sticker.file_unique_id in self._stickers
                or sticker.set_name in self._sets
            )

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
