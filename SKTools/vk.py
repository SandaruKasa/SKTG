from time import sleep

from requests import get

from SKTools import Logger, safeguard
from SKTools.links import vk_api
from SKTools.tokens import vk_params, preaching_room_id


def request(method, **params):
    code = 0  # I honestly don't need this line. I'm adding it only to stop PyCharm's being stupid with the inspection.
    params.update(vk_params)
    res = get(vk_api + method, params=params).json()
    while 'error' in res and (code := res['error']['error_code']) in (6, 429):
        sleep(0.125 if code == 6 else 1)
        res = get(vk_api + method, params=params).json()
    return res


class Reposter:
    def __init__(self, bot, original_group_id, logger=None):
        self.original_group_id = original_group_id
        self.bot = bot
        if logger is None:
            logger = Logger(self.bot, preaching_room_id)
            logger.start()
        self.logger = logger
        from queue import Queue
        self.tasks = Queue()
        from threading import Thread
        Thread(target=self.processor).start()

    def parse_post(self, post, reply):
        from re import sub
        from datetime import datetime
        from json import dumps
        n = post['id']
        link = 'https://vk.com/wall{}_{}'.format(self.original_group_id, n)
        self.logger.log('Parsing {}'.format(link))
        photos = []
        if 'attachments' in post.keys():
            for attach in post['attachments']:
                if attach['type'] == 'photo':
                    sizes = attach['photo']['sizes']
                    sizes.sort(key=lambda size: size['width'] * size['height'])
                    photos.append(sizes[-1]['url'])
        text = post['text']
        if 'signer_id' in post.keys():
            signer = request('users.get', user_ids=post['signer_id'])['response'][0]
        elif post['from_id'] != post['owner_id']:
            signer = request('users.get', user_ids=post['from_id'])['response'][0]
        else:
            signer = None
        for symbol, replacement in (('<', '&lt;'), ('>', '&gt;'), ('&', '&amp;'), ('"', '&quot;')):
            text = replacement.join(text.split(symbol))
        text = sub(r'\[([^|]*)\|([^]]*)\]', r'<a href="https://vk.com/\1">\2</a>', text) + '\n______\n'
        signer = 'by <a href="https://vk.com/id{}">{} {}</a>\n'.format(signer['id'], signer['first_name'],
                                                                       signer['last_name']) if signer else ''
        text += '{}\n{}{}'.format('https://vk.com/wall{}_{}'.format(self.original_group_id, n), signer,
                                  datetime.utcfromtimestamp(post['date']).strftime(r'%Y-%m-%d @ %H:%M UTC'))
        if len(photos) == 0:
            posting_result = self.bot.method('sendMessage', text=text, parse_mode='HTML', **reply)
        elif len(photos) == 1:
            posting_result = self.bot.method('sendPhoto', caption=text, parse_mode='HTML', photo=photos[0], **reply)
        else:
            media = [{'type': 'photo', 'media': photo} for photo in photos]
            media[0]['caption'] = text
            media[0]['parse_mode'] = 'HTML'
            posting_result = self.bot.method('sendMediaGroup', media=dumps(media, ensure_ascii=False), **reply)
        self.logger.log(posting_result, indent=1)
        return n

    def check_old(self, num, reply):
        from json import dumps
        post = request('wall.getById', posts='{}_{}'.format(self.original_group_id, num))
        if 'response' in post.keys() and isinstance(post['response'], list) and post['response']:
            self.parse_post(post['response'][0], reply)
            return True
        else:
            if 'response' not in post.keys() or post['response'] != []:
                traceback = 'https://vk.com/wall{}_{} #was_not_processed. Contents:\n\n{}'.format(
                    self.original_group_id, num, dumps(post, indent=4, ensure_ascii=False))
                self.logger.log(traceback)
                with open('fail_{}_{}.txt'.format(self.original_group_id, num), 'w', encoding='utf-8') as o:
                    o.write(traceback)
            else:
                from os import listdir, getcwd
                self.logger.log('{}_{} was empty.'.format(self.original_group_id, num),
                                send='{}_first.txt'.format(self.original_group_id) in listdir(getcwd()))
            return False

    @safeguard(2, True)
    def do_old(self, reply):
        from os import listdir, getcwd
        prefix = '{}_{}_'.format(self.original_group_id, reply['chat_id'])
        first = '{}_first.txt'.format(self.original_group_id)
        self.logger.log('Searching for old...')
        if prefix + 'old.txt' in listdir(getcwd()):
            with open(prefix + 'old.txt') as o:
                n = int(o.read().strip()) + 1
        else:
            if first in listdir(getcwd()):
                with open(first) as o:
                    n = int(o.read().strip())
            else:
                n = 1
        if prefix + 'lim.txt' in listdir(getcwd()):
            with open(prefix + 'lim.txt') as o:
                lim = int(o.read().strip())
        else:
            lim = 0
            for post in request('wall.get', owner_id=self.original_group_id, count=2)['response']['items']:
                lim = max(lim, post['id'] + 1)
        flag = self.check_old(n, reply) if n < lim else False
        while not flag and (n < lim or lim == -1):
            n += 1
            flag = self.check_old(n, reply)
        with open(prefix + 'old.txt', 'w') as o:
            o.write(str(n))
        if first not in listdir(getcwd()):
            with open(first, 'w') as o:
                o.write(str(n))
        if flag:
            self.logger.log('Old posts processed.')
        else:
            self.logger.log(self.bot.method('sendMessage', text='No more posts left!', **reply))
            self.logger.log('No more old posts left!')

    @safeguard(2, True)
    def do_new(self, reply, count):
        from os import listdir, getcwd
        prefix = '{}_{}_'.format(self.original_group_id, reply['chat_id'])
        self.logger.log('Checking for new...')
        if count is None:
            count = 100 if prefix + 'old.txt' in listdir(getcwd()) else 1
        if prefix + 'new.txt' in listdir(getcwd()):
            with open(prefix + 'new.txt') as o:
                n = int(o.read().strip())
        else:
            n = 0
        posts = request('wall.get', owner_id=self.original_group_id, count=count)['response']['items']
        posts.sort(key=lambda post: post['id'])
        i, a = 0, n
        while i < len(posts) and posts[i]['id'] <= n:
            i += 1
        self.logger.log(
            'Previous: {}.\n\nFresh: {}.'.format((', '.join(str(post['id']) for post in posts[:i]) if i else 'none'), (
                ', '.join(str(post['id']) for post in posts[i:]) if i != len(posts) else 'none')))
        for post in posts[i:]:
            a = self.parse_post(post, reply)
        self.logger.log('New posts processed.')
        if a == n:
            self.do_old(reply)
        else:
            with open(prefix + 'new.txt', 'w') as o:
                o.write(str(a))
            if prefix + 'lim.txt' not in listdir(getcwd()):
                with open(prefix + 'lim.txt', 'w') as o:
                    o.write(str(a))

    def processor(self):
        from time import sleep
        while True:
            if not self.tasks.empty():
                task = self.tasks.get()
                result = self.do_new(*task) if task[1] else self.do_old(task[0])
                if not result[0]:
                    self.logger.log('{}\n{}'.format(repr(task), result[1]))
                self.tasks.task_done()
            else:
                sleep(1 / 4)

    def do(self, target_chat, reply_to=None, new=None):
        reply = {'chat_id': target_chat}
        if reply_to is not None:
            reply['reply_to_message_id'] = reply_to
        self.tasks.put((reply, new))
