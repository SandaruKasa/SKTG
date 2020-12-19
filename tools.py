def safeguard(retries=27, return_error_log=False):
    def safeguard_decorator(func):
        def safeguard_wrapper(*args, **kwargs):
            from datetime import datetime
            r = retries
            error_log = []
            while r:
                try:
                    return (True, func(*args, **kwargs)) if return_error_log else func(*args, **kwargs)
                except Exception as e:
                    error_log.append(str(datetime.now()) + '\n' + '\n'.join(list(map(str, (func, args, kwargs, r, e)))))
                    r = max(-1, r - 1)
            error_log = '\n\n'.join(error_log)
            if return_error_log:
                return False, error_log
            else:
                print(error_log)

        return safeguard_wrapper

    return safeguard_decorator


class Logger:
    def __init__(self, token, destination, default_daemon=False):
        from queue import Queue
        from links import telegram_bot_api
        from threading import Thread
        self.bot = telegram_bot_api.format(token)
        self.queue = Queue()
        self.execute = True
        self.destination = destination
        self.default_daemon = default_daemon
        self.thread = Thread(target=self.executor, daemon=default_daemon)

    def executor(self):
        from links import proxies
        from requests import post
        while self.execute:
            if not self.queue.empty():
                log = self.queue.get()
                if log is None:
                    self.queue.task_done()
                    break

                @safeguard(log[1])
                def send(text):
                    post(self.bot + 'sendMessage', params={'chat_id': self.destination, 'text': text}, proxies=proxies)

                send(log[0])
                self.queue.task_done()

    def run(self):
        return self.thread.run()

    def start(self, delay=0, daemon=None):
        if daemon is None:
            daemon = self.default_daemon
        else:
            self.thread.daemon = daemon
        if delay:
            from time import sleep
            sleep(delay)
        try:
            self.thread.start()
        except RuntimeError as e:
            if self.thread.isAlive():
                raise e
            else:
                from threading import Thread
                self.thread = Thread(target=self.executor, daemon=daemon)
                self.thread.start()

    def join(self, *args, **kwargs):
        self.thread.join(*args, **kwargs)

    def kill(self, delay):
        if delay:
            from time import sleep
            sleep(delay)
        if self.thread.is_alive():
            self.execute = False

    def stop(self, delay=0, timeout=0):
        if delay:
            from time import sleep
            sleep(delay)
        from threading import Thread
        if timeout:
            Thread(target=self.kill, args=(timeout,)).start()
        self.queue.put(None)

    def log(self, text, include_time=True, sep='\n', send=True, retries=27):
        if include_time:
            from datetime import datetime
            text = '{}{}{}'.format(datetime.now().strftime(r'%H:%M:%S'), sep, text)
        print(text)
        if send:
            self.queue.put((text, retries))

    def is_alive(self):
        return self.thread.is_alive()

    def is_daemon(self):
        return self.thread.isDaemon()
