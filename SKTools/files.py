#!/usr/bin/env python3
from json import load, dump
from os import getcwd, listdir, remove, mkdir
from os.path import join, isfile, isdir, exists, isabs, split
from threading import Thread, RLock
from time import time
from typing import Optional, Callable, Iterator, Tuple, Union, Any


def split_path(path: str) -> Tuple[str, ...]:
    s = split(path)
    return tuple(i for i in (split_path(s[0]) + (s[-1],) if s[-1] else (s[0],)) if i)


def join_path(*parts: Union[Iterator[str], str]) -> str:
    p = []
    for part in parts:
        if isinstance(part, str):
            p.append(part)
        else:
            for i in part:
                p.append(i)
    return join(*p)


def pave_path(path: str) -> None:
    if not exists(path):
        if not isabs(path):
            path = join_path(getcwd(), path)
        path = split_path(path)
        c = ''
        for i in path:
            c = join_path(c, i)
            if not exists(c):
                try:
                    mkdir(c)
                except FileExistsError:
                    # in case it has already been created in another thread
                    pass


def sk_open(file_name: str, mode: str = 'r',
            buffering: int = -1, encoding: Optional[str] = 'utf-8',
            errors: Optional[str] = None, newline: Optional[str] = None,
            closefd: Optional[bool] = True, opener: Optional[Callable] = None):
    if 'b' in mode:
        encoding = None
    if 'w' in mode or 'a' in mode:
        p = split_path(file_name)
        if len(p) > 1:
            pave_path(join_path(p[:-1]))

    return open(file=file_name, mode=mode, buffering=buffering, encoding=encoding,
                errors=errors, newline=newline, closefd=closefd, opener=opener)


def folder_walker(cur_path: str = getcwd(), yield_files: bool = True, yield_directories: bool = False) -> Iterator[str]:
    try:
        if isfile(cur_path):
            if yield_files:
                yield cur_path
        elif isdir(cur_path):
            if yield_directories:
                yield cur_path
            for new_path in map(lambda x: join(cur_path, x), listdir(cur_path)):
                yield from folder_walker(new_path, yield_files, yield_directories)
        else:
            print('Unknown problem:', cur_path)
    except FileNotFoundError:
        print('Not found:', cur_path)
    except PermissionError:
        print('No permission:', cur_path)


def remove_file(file_name: str) -> None:
    from SKTools import safeguard

    @safeguard(8)
    def remove_file_core() -> None:
        remove(file_name)

    Thread(target=remove_file_core, daemon=False).start()


def change_extension(old_file_name: str, new_extension: str, sep: str = '.') -> str:
    return f'{sep.join(old_file_name.split(sep)[:-1]) if sep in split_path(old_file_name)[-1] else old_file_name}' \
           + f'{sep}{new_extension}'


class CachedSet(set):
    def __init__(self, file_name: Optional[str] = None):
        self._file_name = f'{time()}.json' if file_name is None else file_name
        self._lock = RLock()
        with self._lock:
            if exists(self._file_name):
                with sk_open(self._file_name) as f:
                    super().__init__(load(f))
            else:
                super().__init__()

    def _write(self) -> None:
        def write_core():
            with self._lock, sk_open(self._file_name, 'w') as f:
                dump(list(self), f, ensure_ascii=False, indent=2)

        Thread(target=write_core).start()

    def add(self, item: Union[str, int]) -> None:
        item = int(item)
        with self._lock:
            if item not in self:
                super().add(item)
                self._write()

    def remove(self, item: Union[str, int]):
        item = int(item)
        with self._lock:
            if item in self:
                super().remove(item)
                self._write()


class CachedDict(dict):
    def __init__(self, file_name: Optional[str] = None):
        self._file_name = f'{time()}.json' if file_name is None else file_name
        self._lock = RLock()
        with self._lock:
            if exists(self._file_name):
                with sk_open(self._file_name) as f:
                    super().__init__(load(f))
            else:
                super().__init__()

    def _write(self) -> None:
        def write_core():
            with self._lock, sk_open(self._file_name, 'w') as f:
                dump(self, f, ensure_ascii=False, indent=2)

        Thread(target=write_core).start()

    def __contains__(self, key) -> bool:
        return super().__contains__(str(key))

    def __getitem__(self, key):
        return super().__getitem__(str(key))

    def __setitem__(self, key, value) -> None:
        with self._lock:
            if key not in self or self[key] != value:
                super().__setitem__(str(key), value)
                self._write()

    def get(self, key, default=None) -> Any:
        return super().get(str(key), default)

    def pop(self, k) -> Any:
        with self._lock:
            res = super().pop(str(k))
            self._write()
        return res

    def popitem(self) -> Tuple[str, Any]:
        with self._lock:
            res = super().popitem()
            self._write()
        return res

    def setdefault(self, key, default=None) -> Any:
        with self._lock:
            if key in self:
                return self[key]
            else:
                self[key] = default
                return default

    def clear(self) -> None:
        with self._lock:
            super().clear()
            self._write()
