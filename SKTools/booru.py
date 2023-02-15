#!/usr/bin/env python3
from random import randint
from typing import Optional, Callable
from xml.etree.ElementTree import fromstring, Element

import requests

from SKTools.files import remove_file
from SKTools.links import booru_api
from SKTools.tg import Bot, reply_dict


class Booru:
    def __init__(self, booru_name: str):
        self._api_link = booru_api.format(booru_name)

    def method(self, **params) -> Element:
        return fromstring(requests.get(self._api_link, params=params).text)

    def search(self, tags: str = '', limit: int = 100, pid: int = 0) -> Element:
        return self.method(page='dapi', s='post', q='index', tags=tags, limit=limit, pid=pid)

    def count(self, tags: str) -> int:
        return int(self.search(tags, limit=0).attrib['count'])

    def get_post_by_offset(self, tags: str, n: int) -> dict:
        return self.search(tags, limit=1, pid=n)[0].attrib

    def get_random_post(self, tags: str) -> Optional[dict]:
        total = self.count(tags=tags)
        return self.get_post_by_offset(tags=tags, n=randint(0, min(20_000, total - 1))) if total else None

    def download_file_by_url(self, file_url: str) -> str:
        file_name = file_url.split('/')[-1]
        requests.get(file_url)
        with open(file_name, 'wb') as file:
            file.write(r.content)
        return file_name

    @staticmethod
    def _default_determiner(post: dict) -> bool:
        return post['file_url'].split('.')[-1].lower() not in ('jpg', 'jpeg', 'png') \
               or int(post['height']) >= 1920 or int(post['width']) >= 1920

    def count_for_telegram(self, bot: Bot, msg: dict):
        bot.sendMessage(f"{self.count(' '.join(msg['text'].split()[1:])):,}".replace(',', ' '), **reply_dict(msg))

    def process_search_query_from_telegram(self, bot: Bot, msg: dict, doc_requested: bool = False,
                                           determiner_whether_the_file_should_be_sent_as_a_document:
                                           Optional[Callable[[dict], bool]] = None) -> None:
        reply = reply_dict(msg)
        post = self.get_random_post(' '.join(msg['text'].split()[1:]))
        if post is None:
            bot.sendMessage('Nothing found', **reply)
        else:
            if determiner_whether_the_file_should_be_sent_as_a_document is None:
                determiner_whether_the_file_should_be_sent_as_a_document = self._default_determiner
            caption = f'Taken from: {self._api_link}?page=post&s=view&id={post["id"]}'
            if doc_requested or determiner_whether_the_file_should_be_sent_as_a_document(post):
                file_name = self.download_file_by_url(post['file_url'])
                bot.sendDocument(file_name, caption=caption, **reply)
                remove_file(file_name)
            else:
                bot.sendPhoto(photo=post['file_url'], caption=caption, **reply)
        # todo: localizations
