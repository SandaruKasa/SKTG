#!/usr/bin/env python3
from datetime import datetime
from json import dumps
from queue import Queue
from threading import Thread, Lock
from time import sleep, perf_counter, time
from traceback import format_tb
from types import TracebackType
from typing import Union, Optional, Tuple, Callable, Any, Sequence, List, Dict


def altdiv(dividend: int, divisor: int) -> int:
    return (dividend - 1) // divisor + 1


def split_into_parts(sequence: Sequence, /, max_part_len: int) -> List[Sequence]:
    return [sequence[offset_multiplier * max_part_len:(offset_multiplier + 1) * max_part_len]
            for offset_multiplier in range(altdiv(len(sequence), max_part_len))]


class RetriesLog(dict):
    def __init__(self, observed_function: Optional[Callable] = None,
                 args: Optional[tuple] = None, kwargs: Optional[dict] = None):
        super().__init__({'observed_function': observed_function, 'args': args, 'kwargs': kwargs})
        self['success'] = self.success = None
        self['result'] = self.result = None
        self['log'] = []

    def __enter__(self):
        pass

    def __exit__(self, et, ev, tb):
        # todo
        self['log'].append({'datetime': datetime.now(), 'exception_type': et, 'exception_value': ev, 'traceback': tb})

    def finalize(self, success: bool, result: Any) -> None:
        self['success'] = self.success = success
        self['result'] = self.result = result

    @staticmethod
    def JSON_serializer(obj):
        if isinstance(obj, TracebackType):
            return '\n'.join(format_tb(obj))
        else:
            return str(obj)

    def __str__(self):
        return dumps(self, ensure_ascii=False, indent=4, default=self.JSON_serializer)


def safeguard(attempts: int = 27, return_log: bool = False):
    def safeguard_decorator(func):
        def safeguard_wrapper(*args, **kwargs) -> Union[Any, RetriesLog]:
            retries_left = attempts
            log = RetriesLog(func, args, kwargs)
            success = False
            result = None
            while retries_left and not success:
                try:
                    with log:
                        result = func(*args, **kwargs)
                        success = True
                except:
                    pass
                finally:
                    retries_left = max(-1, retries_left - 1)
            log.finalize(success, result)
            if return_log:
                return log
            else:
                if not success:
                    print(log)
                return result

        return safeguard_wrapper

    return safeguard_decorator


def stopwatch(func):
    def stopwatch_wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        print(f"Finished {func.__name__} in {end_time - start_time:.27f} secs")
        return result

    return stopwatch_wrapper


class Processor:
    TASK = Any
    TIME_MEASURE = Union[int, float, None]

    def __init__(self, processing_function: Optional[Callable[[TASK], None]] = None,
                 start_right_after_initialization: bool = True, default_daemon: bool = False,
                 queue_sleeping_delay: TIME_MEASURE = None):
        class ExecutionStopperDummy:
            pass

        self._processing_function = processing_function
        self._keep_running = start_right_after_initialization
        self.queue = Queue()
        self._default_daemon = default_daemon
        self._queue_sleeping_delay = 1 / 4 if queue_sleeping_delay is None else queue_sleeping_delay
        self._execution_stopper_dummy = ExecutionStopperDummy()
        self._execution_thread = Thread(target=self._core, daemon=default_daemon)
        self.start()

    def processing_function(self, task: TASK) -> None:
        self._processing_function(task)

    def _core(self) -> None:
        while self._keep_running:
            if not self.queue.empty():
                task = self.queue.get()
                if task is self._execution_stopper_dummy:
                    self._keep_running = False
                else:
                    self.processing_function(task)
                self.queue.task_done()
            else:
                sleep(self._queue_sleeping_delay)

    def start(self, delay: TIME_MEASURE = 0, daemon: Optional[bool] = None,
              queue_sleeping_delay: Optional[bool] = None) -> None:
        if daemon is None:
            daemon = self._default_daemon
        if queue_sleeping_delay is not None:
            self._queue_sleeping_delay = queue_sleeping_delay
        if delay:
            sleep(delay)
        try:
            self._execution_thread.start()
        except RuntimeError as e:
            if self._execution_thread.is_alive():
                raise e
            else:
                self._execution_thread = Thread(target=self._core, daemon=daemon)
                self._execution_thread.start()

    def kill(self, delay: TIME_MEASURE = 0) -> None:
        if delay:
            sleep(delay)
        if self._execution_thread.is_alive():
            self._keep_running = False

    def stop(self, delay: TIME_MEASURE = 0, timeout: TIME_MEASURE = 0) -> None:
        if delay:
            sleep(delay)
        if timeout:
            Thread(target=self.kill, args=(timeout,)).start()
        self.queue.put(self._execution_stopper_dummy)

    def put(self, task: TASK) -> None:
        self.queue.put(task)

    add = put

    def is_alive(self) -> bool:
        return self._execution_thread.is_alive()

    def is_daemon(self) -> bool:
        return self._execution_thread.isDaemon()

    def join(self, timeout: TIME_MEASURE = None):
        self.stop()
        self._execution_thread.join(timeout)


class Logger(Processor):
    TASK = dict

    def __init__(self, bot=None, destination: Union[str, int, None] = None, default_daemon: bool = False,
                 queue_sleeping_delay: Processor.TIME_MEASURE = 1 / 4, default_file_name: Optional[str] = None,
                 start_right_after_initialization: bool = True):
        self.bot = bot
        self.destination = destination
        self.telegram = self.bot and self.destination
        if self.telegram:
            super().__init__(start_right_after_initialization=start_right_after_initialization,
                             default_daemon=default_daemon, queue_sleeping_delay=queue_sleeping_delay)
        self.default_file_name = default_file_name or f'{time()}.sklog'
        self.locks = {}

    def processing_function(self, task: TASK) -> None:
        self.bot.sendMessage(task['text'], chat_id=self.destination, **task['params'])

    def start(self, delay: Processor.TIME_MEASURE = 0, daemon: Optional[bool] = None,
              queue_sleeping_delay: Optional[bool] = None) -> None:
        if self.telegram:
            super().start(delay, daemon, queue_sleeping_delay)

    def kill(self, delay: Processor.TIME_MEASURE = 0) -> None:
        if self.telegram:
            super().kill(delay)

    def stop(self, delay: Processor.TIME_MEASURE = 0, timeout: Processor.TIME_MEASURE = 0) -> None:
        if self.telegram:
            super().stop(delay, timeout)

    @staticmethod
    def _default_json_serializer(obj: Any):
        if isinstance(obj, set):
            obj = list(obj)
            try:
                obj.sort()
            except TypeError:
                pass
            finally:
                return obj
        else:
            return {'repr': repr(obj), 'str': str(obj)}

    def log(self, *text, sep: str = '\n', include_time: bool = True, send: bool = True, indent: int = 4,
            json_serializer: Optional[Callable] = None, use_file: bool = True, file_name: Optional[str] = None,
            use_logs_subdir: bool = True, tg_params: Optional[Dict[str, Any]] = None) -> str:
        from SKTools.files import sk_open, join_path
        text = list((datetime.now().strftime(r'%H:%M:%S'),) + text if include_time else text)
        if json_serializer is None:
            json_serializer = self._default_json_serializer
        for i in range(len(text)):
            if not isinstance(text[i], str):
                text[i] = dumps(text[i], indent=indent, ensure_ascii=False, default=json_serializer)
        text = sep.join(text)
        print(text + '\n')
        if self.telegram and send:
            self.add({'text': text, 'params': tg_params or {}})
        if use_file:
            if file_name is None:
                file_name = self.default_file_name
            if '.' not in file_name:
                file_name += '.sklog'
            if use_logs_subdir:
                file_name = join_path('logs', file_name)
            with sk_open(file_name, 'a') as log_file, self.locks.setdefault(file_name, Lock()):
                log_file.write(text + '\n')
        return text

    def is_alive(self) -> Optional[bool]:
        return super().is_alive() if self.telegram else None

    def is_daemon(self) -> Optional[bool]:
        return super().is_daemon() if self.telegram else None

    def join(self, timeout: Processor.TIME_MEASURE = None) -> None:
        if self.telegram:
            super().join(timeout)


Types = Union[type, Tuple[type, ...]]


def recursive_applier(obj, function_to_apply, applicable_types: Types,
                      iteration_whitelist: Types = (), iteration_blacklist: Types = ()):
    """
    This bad boy recursively applies a function to an object.

    At first it checks if obj is an instance of applicable_types. If it is, then function_to_apply(obj) is returned.
    If it is not, obj is checked to be a dictionary. If it is, all its values undergo the same process.
    If it is not, then obj is checked to be iterable. If it is, the map of recursive_applier and iter(obj) is returned
    (in case obj was a list or a tuple, the map is converted back to a list or a tuple respectively).
    If it is not, the obj is returned without any changes.

    Note that the function_to_apply won't be applied to its results.
    :param obj: self-explanatory
    :param function_to_apply: self-explanatory
    :param applicable_types: a type or a tuple of types that function_to_apply can be applied to
    :param iteration_whitelist: a tuple of types; if not empty, only objects of given types will be iterated
    :param iteration_blacklist: a tuple of types; if not empty, objects of given types will not be iterated
    :return: the result if recursive function applying as describes above
    """
    if isinstance(obj, applicable_types):
        return function_to_apply(obj)
    elif isinstance(obj, dict):
        for i in obj:
            obj[i] = recursive_applier(obj[i], function_to_apply, applicable_types,
                                       iteration_whitelist, iteration_blacklist)
        return obj
    else:
        try:
            if iteration_whitelist and not isinstance(obj, iteration_whitelist) or \
                    iteration_blacklist and isinstance(obj, iteration_blacklist):
                raise TypeError
            iterator = iter(obj)
        except TypeError:
            return obj
        else:
            res = map(lambda x: recursive_applier(x, function_to_apply, applicable_types,
                                                  iteration_whitelist, iteration_blacklist),
                      iterator)
            return obj.__class__(res) if isinstance(obj, (tuple, list)) else res
