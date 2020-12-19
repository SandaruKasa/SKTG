from SKTools.links import telegram_bot_api


def altdiv(dividend: int, divisor: int) -> int:
    return (dividend - 1) // divisor + 1


def safeguard(retries=27, return_error_log=False):
    class ErrorLog(list):
        def __str__(self):
            return '\n\n'.join(str(e[0]) + '\n' + '\n'.join(map(repr, e[1:])) for e in self) + '\n'

    def safeguard_decorator(func):
        def safeguard_wrapper(*args, **kwargs):
            from datetime import datetime
            r = retries
            error_log = ErrorLog()
            while r:
                try:
                    return (True, func(*args, **kwargs)) if return_error_log else func(*args, **kwargs)
                except Exception as e:
                    error_log.append((datetime.now(), func, args, kwargs, r, e))
                    r = max(-1, r - 1)
            if return_error_log:
                return False, error_log
            else:
                print(error_log)

        return safeguard_wrapper

    return safeguard_decorator


class Logger:
    def __init__(self, bot=None, destination=None, default_daemon=False, queue_sleeping_delay=1 / 4):
        self.bot = bot
        self.destination = destination
        self.telegram = self.bot and self.destination
        self.execute = self.telegram
        if self.telegram:
            from queue import Queue
            from threading import Thread
            self.queue = Queue()
            self.default_daemon = default_daemon
            self.queue_sleeping_delay = queue_sleeping_delay
            self.thread = Thread(target=self.executor, daemon=default_daemon)

    def executor(self):
        from time import sleep
        while self.execute:
            if not self.queue.empty():
                log = self.queue.get()
                if log is None:
                    self.queue.task_done()
                    break
                self.bot.method('sendMessage', chat_id=self.destination, text=log[0])
                self.queue.task_done()
            else:
                sleep(self.queue_sleeping_delay)

    def start(self, delay=0, daemon=None, queue_sleeping_delay=None):
        if self.telegram:
            if daemon is None:
                daemon = self.default_daemon
            if queue_sleeping_delay is not None:
                self.queue_sleeping_delay = queue_sleeping_delay
            if delay:
                from time import sleep
                sleep(delay)
            try:
                self.thread.start()
            except RuntimeError as e:
                if self.thread.is_alive():
                    raise e
                else:
                    from threading import Thread
                    self.thread = Thread(target=self.executor, daemon=daemon)
                    self.thread.start()

    def kill(self, delay):
        if self.telegram:
            if delay:
                from time import sleep
                sleep(delay)
            if self.thread.is_alive():
                self.execute = False

    def stop(self, delay=0, timeout=0):
        if self.telegram:
            if delay:
                from time import sleep
                sleep(delay)
            from threading import Thread
            if timeout:
                Thread(target=self.kill, args=(timeout,)).start()
            self.queue.put(None)

    def log(self, *text, sep='\n', include_time=True, send=True, retries=27, indent=4):
        if include_time:
            from datetime import datetime
            text = (datetime.now().strftime(r'%H:%M:%S'),) + text
        from json import dumps
        text = sep.join(i if isinstance(i, str) else dumps(i, indent=indent, ensure_ascii=False) for i in text)
        print(text + '\n')
        if self.telegram and send:
            self.queue.put((text, retries))

    def is_alive(self):
        return self.telegram and self.thread.is_alive()

    def is_daemon(self):
        return self.thread.isDaemon() if self.telegram else None


def remove_file(file_name):
    from os import remove
    from threading import Thread

    @safeguard(8)
    def remove_file_core():
        remove(file_name)

    Thread(target=remove_file_core).start()
