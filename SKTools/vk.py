#!/usr/bin/env python3
from datetime import datetime
from json import dumps
from os.path import join, exists
from random import sample
from re import sub
from time import sleep
from typing import Optional, Tuple, Dict

from requests import get

from SKTools import Logger, safeguard, recursive_applier, RetriesLog, Processor
from SKTools.files import sk_open
from SKTools.links import vk_api
from SKTools.tg import Bot, html_encode
from SKTools.tokens import vk_token, preaching_room_id

vk_params = {'v': '5.103', 'access_token': vk_token}


@safeguard(2)
def method(method_name: str, **params) -> dict:
    params.update(vk_params)
    res = get(vk_api + method_name, params=params).json()
    while 'error' in res and (code := res['error']['error_code']) in (6, 429):
        sleep(0.125 if code == 6 else 1)
        res = get(vk_api + method_name, params=params).json()
    try:
        return res['response']
    except KeyError:
        raise Exception(Logger().log(res))


class Reposter(Processor):
    NUMBER = Optional[int]
    REPLY = Dict[str, int]
    TASK = Tuple[REPLY, NUMBER]

    def __init__(self, bot: Bot, original_group_id: int, logger: Optional[Logger] = None,
                 start_right_after_initialization: bool = True, default_daemon: bool = False,
                 queue_sleeping_delay: Processor.TIME_MEASURE = None):
        self.original_group_id = original_group_id
        self.bot = bot
        self.logger = Logger(self.bot, preaching_room_id) if logger is None else logger
        super().__init__(start_right_after_initialization=start_right_after_initialization,
                         default_daemon=default_daemon, queue_sleeping_delay=queue_sleeping_delay)

    @staticmethod
    def _parse_attachment(attachment: dict) -> Optional[Tuple[str, str]]:
        t = attachment['type']
        attachment = attachment[t]
        if t in ('page', 'album', 'photos_list', 'market', 'market_album', 'pretty_cards', 'event'):
            return
        elif t in ('posted_photo', 'graffiti', 'app'):
            return 'photo', attachment['photo_604']
        elif t in ('photo', 'sticker'):
            return t, max(attachment['sizes' if t == 'photo' else 'images_with_background'],
                          key=lambda size: size['width'] * size['height'])['url']
        elif t == 'video':
            return t, f'<a href="{attachment["player"]}">{attachment["title"]}</a>'
        elif t == 'audio':
            return t, f'{attachment["artist"]} — {attachment["title"]}'
        elif t == 'doc':
            return  # todo: https://vk.com/dev/objects/doc
        elif t == 'link':
            return t, f'<a href="{attachment["url"]}">{attachment["title"]} - {attachment["description"]}</a>'
        elif t == 'note':
            return  # todo: https://vk.com/dev/objects/note
        elif t == 'poll':
            return  # todo: https://vk.com/dev/objects/poll
        elif t == 'doc':
            return  # todo: https://vk.com/dev/objects/doc

    def parse_post(self, post: dict, reply: dict) -> int:
        n = post['id']
        link = f'https://vk.com/wall{self.original_group_id}_{n}'
        self.logger.log(f'Parsing {link}', send=False)
        photos = []
        if 'attachments' in post.keys():
            for attach in post['attachments']:
                if attach['type'] == 'photo':
                    photos.append(max(attach['photo']['sizes'], key=lambda size: size['width'] * size['height'])['url'])
        text = html_encode(post['text'])
        text = sub(r'\[([^|]*)\|([^]]*)\]', r'<a href="https://vk.com/\1">\2</a>', text) + '\n______\n'
        if 'signer_id' in post.keys():
            author = method('users.get', user_ids=post['signer_id'])[0]
        elif post['from_id'] != post['owner_id']:
            author = method('users.get', user_ids=post['from_id'])[0]
        else:
            author = None
        author = recursive_applier(author, html_encode, str)
        author = 'by <a href="https://vk.com/id{id}">{first_name} {last_name}</a>\n'.format(**author) if author else ''
        text += f'{link}\n{author}{datetime.utcfromtimestamp(post["date"]).strftime(r"%Y-%m-%d @ %H:%M UTC")}'
        if len(photos) == 0:
            posting_result = self.bot.sendMessage(text, parse_mode='HTML', **reply)
        elif len(photos) == 1:
            posting_result = self.bot.sendPhoto(caption=text, parse_mode='HTML', photo=photos[0], **reply)
        else:
            media = [{'type': 'photo', 'media': photo} for photo in photos]
            media[0]['caption'] = text
            media[0]['parse_mode'] = 'HTML'
            posting_result = self.bot.method('sendMediaGroup', media=dumps(media, ensure_ascii=False), **reply)
        self.logger.log(posting_result, send=False)
        return n

    def _get_newest_id(self) -> int:
        res = 0
        for post in method('wall.get', owner_id=self.original_group_id, count=2)['items']:
            res = max(res, post['id'])
        return res

    def check_post(self, num: int, reply: dict) -> bool:
        post = method('wall.getById', posts='{}_{}'.format(self.original_group_id, num))
        if isinstance(post, list):
            if post:
                self.parse_post(post[0], reply)
                return True
            else:
                self.logger.log(f'{self.original_group_id}_{num} was empty.', send=False)
                return False
        else:
            traceback = f'https://vk.com/wall{self.original_group_id}_{num} #was_not_processed. Contents:\n\n' + \
                        dumps(post, indent=4, ensure_ascii=False)
            self.logger.log(traceback, file_name=f'vk_fail_{self.original_group_id}_{num}.txt')
            return False

    @safeguard(2, True)
    def do_old(self, reply: dict) -> RetriesLog:
        prefix = join('vk', f'{self.original_group_id}_{reply["chat_id"]}_')
        first_name = join('vk', f'{self.original_group_id}_first.txt')
        old_name = prefix + 'old.txt'
        lim_name = prefix + 'lim.txt'
        self.logger.log('Searching for old...', send=False)
        if exists(old_name):
            with sk_open(old_name) as o:
                n = int(o.read().strip()) + 1
        elif exists(first_name):
            with sk_open(first_name) as o:
                n = int(o.read().strip())
        else:
            n = 1
        if exists(lim_name):
            with sk_open(lim_name) as o:
                lim = int(o.read().strip())
        else:
            lim = self._get_newest_id() + 1
        flag = False
        while not flag and n < lim:
            flag = self.check_post(n, reply)
            n += 1
        with sk_open(old_name, 'w') as o:
            o.write(str(n - 1))
        if not exists(first_name):
            with sk_open(first_name, 'w') as o:
                o.write(str(n - 1))
        if flag:
            self.logger.log('Old posts processed.', send=False)
        else:
            self.logger.log(self.bot.sendMessage('No more posts left!', **reply))

    @safeguard(2, True)
    def do_new(self, reply: dict, count: NUMBER = None) -> RetriesLog:
        prefix = join('vk', f'{self.original_group_id}_{reply["chat_id"]}_')
        old_name = prefix + 'old.txt'
        new_name = prefix + 'new.txt'
        lim_name = prefix + 'lim.txt'
        self.logger.log('Checking for new...', send=False)
        if count is None:
            count = 100 if exists(new_name) or exists(old_name) else 1
        if exists(new_name):
            with sk_open(new_name) as o:
                n = int(o.read().strip())
        else:
            n = 0
        posts = method('wall.get', owner_id=self.original_group_id, count=count)['items']
        posts.sort(key=lambda post: post['id'])
        i, a = 0, n
        while i < len(posts) and posts[i]['id'] <= n:
            i += 1
        self.logger.log(
            'Previous: {}.\n\nFresh: {}.'.format((', '.join(str(post['id']) for post in posts[:i]) if i else 'none'), (
                ', '.join(str(post['id']) for post in posts[i:]) if i != len(posts) else 'none')), send=False)
        for post in posts[i:]:
            a = self.parse_post(post, reply)
        self.logger.log('New posts processed.', send=False)
        if a == n:
            self.do_old(reply)
        else:
            with sk_open(new_name, 'w') as o:
                o.write(str(a))
            if not exists(lim_name):
                with sk_open(lim_name, 'w') as o:
                    o.write(str(a))

    def do_search(self, reply: dict, query: str) -> NUMBER:
        count = method('wall.search', owner_id=self.original_group_id, query=query, count=0)['count']
        if count:
            q = sample(range(count), count)
            for i in q:
                post = method('wall.search', owner_id=self.original_group_id, query=query,
                              count=1, offset=i)['items'][0]
                if post['post_type'] == 'post':
                    return self.parse_post(post, reply)
        return None

    def do_random(self, reply) -> NUMBER:
        n = self._get_newest_id()
        q = sample(range(n), n)
        for i in q:
            if self.check_post(i, reply):
                return i
        return None

    def processing_function(self, task: TASK) -> None:
        result = self.do_new(*task) if task[1] else self.do_old(task[0])
        if not result.success:
            self.logger.log(repr(task), result, sep='\n')

    def do(self, chat_id: int, reply_to_message_id: Optional[int] = None,
           number_of_new_posts_to_check: NUMBER = None) -> None:
        reply = {'chat_id': chat_id}
        if reply_to_message_id is not None:
            reply['reply_to_message_id'] = reply_to_message_id
        self.put((reply, number_of_new_posts_to_check))
