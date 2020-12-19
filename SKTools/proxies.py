#!/usr/bin/env python3
from queue import Queue
from random import sample
from threading import Event, Thread
from typing import Optional, Dict, Union, Sequence, Callable

from requests import get, post, Response

from SKTools import split_into_parts
from SKTools.proxylist import https_proxy_list


def get_proxy(threads: int = 100, timeout: int = 5, testing_address: str = 'https://gelbooru.com',
              source: Sequence[str] = https_proxy_list) -> Optional[Dict[str, str]]:
    try:
        if get(testing_address).status_code == 200:
            return None
    except:
        pass
    https_proxies = sample(source, (proxies_to_check := len(source) + 1) - 1)
    threads = proxies_to_check if threads <= 0 else threads

    def select() -> Union[str, bool]:
        nonlocal proxies_to_check
        for portion in split_into_parts(https_proxies, threads):
            q = Queue()

            def check(proxy: str) -> None:
                try:
                    check_res = int(get(testing_address, proxies={'https': proxy}, timeout=timeout).status_code)
                except Exception as e:
                    check_res = e
                q.put((proxy, check_res))

            for p in portion:
                Thread(target=check, args=(f'https://{p}',), daemon=True).start()
            lim = len(portion)
            while lim:
                if q.empty():
                    pass
                else:
                    lim -= 1
                    z = q.get()
                    if z[1] == 200:
                        return z[0]
                    print(proxies_to_check := proxies_to_check - 1, z[0])
                    q.task_done()
        return False

    print(res := get_proxy(threads, timeout, testing_address, source) if (selected := select()) is False else selected)
    return {'https': res}


class ProxiedRequester:
    def __init__(self, default_testing_address: str = 'https://gelbooru.com'):
        self._proxies = None
        self._proxies_can_be_used = Event()
        self._dta = default_testing_address
        Thread(target=self.update_proxies).start()

    def update_proxies(self, threads: int = 100, timeout: int = 5, testing_address: Optional[str] = None) -> None:
        self._proxies_can_be_used.clear()
        self._proxies = get_proxy(threads=threads, timeout=timeout,
                                  testing_address=self._dta if testing_address is None else testing_address)
        self._proxies_can_be_used.set()

    def request(self, requester: Callable[..., Response], address: str, **kwargs) -> Optional[Response]:
        f = 7
        while True:
            try:
                self._proxies_can_be_used.wait()
                kwargs['proxies'] = self._proxies
                return requester(address, **kwargs)
            except Exception as e:
                if self._proxies_can_be_used.is_set():
                    self.update_proxies()
                else:
                    self._proxies_can_be_used.wait()
                if f:
                    f -= 1
                else:
                    raise e

    def get(self, address: str, **kwargs) -> Optional[Response]:
        return self.request(get, address=address, **kwargs)

    def post(self, address: str, **kwargs) -> Optional[Response]:
        return self.request(post, address=address, **kwargs)
