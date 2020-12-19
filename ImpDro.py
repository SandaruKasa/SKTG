from datetime import datetime
from json import dumps
from os import listdir, getcwd, chdir, mkdir
from queue import Queue
from re import sub
from threading import Thread
from time import sleep

import requests as r

from links import *
from tokens import imperial_drone_token, preaching_room_id, target_chat_id, original_group_id, vk_params

bot = telegram_bot_api.format(imperial_drone_token)


def dictsum(a, b):
    a.update(b)
    return a


def hour():
    return datetime.now().hour


def safeguard(target, args=(), kwargs=None, retries=20):
    if kwargs is None:
        kwargs = {}
    errlog = []
    while retries:
        try:
            return True, target(*args, **kwargs)
        except Exception as e:
            errlog.append(str(datetime.now()) + '\n' + '\n'.join(list(map(repr, (target, args, kwargs, retries, e)))))
            retries = max(-1, retries - 1)
    return False, '\n\n'.join(errlog)


def preacher():
    while True:
        if not praying_queue.empty():
            prayer = praying_queue.get()
            if prayer is None:
                break
            safeguard(r.post, (bot + 'sendMessage',),
                      {'params': {'chat_id': preaching_room_id, 'text': prayer}, 'proxies': proxies})
            praying_queue.task_done()


def log(text):
    print(text)
    praying_queue.put(text)


def post_post(link, text, photos, time):
    text = sub(r'\[([^|]*)\|([^]]*)\]', r'<a href="https://vk.com/\1">\2</a>', text) + \
           '\n______\n{}\n{}'.format(link, datetime.utcfromtimestamp(time).strftime(r'%Y-%m-%d @ %H:%M UTC'))
    if len(photos) == 0:
        posting_result = safeguard(r.post, (bot + 'sendMessage',),
                                   {'params': {'chat_id': target_chat_id, 'caption': text, 'parse_mode': 'HTML'},
                                    'proxies': proxies})[1]
    elif len(photos) == 1:
        posting_result = safeguard(r.post, (bot + 'sendPhoto',),
                                   {'params': {'chat_id': target_chat_id, 'caption': text, 'parse_mode': 'HTML',
                                               'photo': photos[0]},
                                    'proxies': proxies})[1]
    else:
        media = [{'type': 'photo', 'media': photo} for photo in photos]
        media[0]['caption'] = text
        media[0]['parse_mode'] = 'HTML'
        posting_result = safeguard(r.post, (bot + 'sendMediaGroup',),
                                   {'params': {'chat_id': target_chat_id, 'media': dumps(media)}, 'proxies': proxies})[
            1]
    log(dumps(posting_result.json(), indent=1))


def parse_post(post):
    n = post['id']
    link = 'https://vk.com/wall{}_{}'.format(original_group_id, n)
    log('Parsing {}'.format(link))
    photos = []
    if 'attachments' in post.keys():
        for attach in post['attachments']:
            if attach['type'] == 'photo':
                sizes = attach['photo']['sizes']
                sizes.sort(key=lambda size: size['width'] * size['height'])
                photos.append(sizes[-1]['url'])
    post_post(link, ''.join(post['text'].split('#Homestuck')), photos, post['date'])
    return n


def check_new(last_post_no):
    posts = safeguard(r.get, (vk_api + 'wall.get',),
                      {'params': dictsum(vk_params, {'owner_id': original_group_id, 'count': 16})})[1].json()[
        'response']['items']
    posts.sort(key=lambda post: post['id'])
    i = 0
    while i < len(posts) and posts[i]['id'] <= last_post_no:
        i += 1
    log('Previous: {}.\n\nFresh: {}.'.format((', '.join(str(post['id']) for post in posts[:i]) if i else 'none'), (
        ', '.join(str(post['id']) for post in posts[i:]) if i != len(posts) else 'none')))
    for post in posts[i:]:
        last_post_no = parse_post(post)
    return last_post_no


def check_old(num):
    post = safeguard(r.get, (vk_api + 'wall.getById',),
                     {'params': dictsum(vk_params, {'posts': '{}_{}'.format(original_group_id, num)})})[1].json()
    if 'response' in post.keys() and type(post['response']) == type([]) and \
            post['response'] and post['response'][0]['from_id'] == original_group_id:
        parse_post(post['response'][0])
        return True
    else:
        traceback = 'https://vk.com/wall{}_{} #was_not_processed. Contents:\n\n{}'.format(original_group_id, num,
                                                                                          dumps(post, indent=4))
        log(traceback)
        with open('{}.txt'.format(num), 'w', encoding='utf-8') as o:
            o.write(traceback)
        return False


def do_new():
    log('Checking for new...')
    if 'new.txt' in listdir(getcwd()):
        with open('new.txt') as o:
            n = int(o.read().strip())
    else:
        n = 0
    n = check_new(n)
    with open('new.txt', 'w') as o:
        o.write(str(n))
    log('New posts processed.')


def do_old():
    lim = 19395
    log('Searching for old...')
    if 'old.txt' in listdir(getcwd()):
        with open('old.txt') as o:
            n = int(o.read().strip())
    else:
        n = 0
    flag = False
    while not flag and n < lim:
        flag = check_old(n)
        n += 1
    with open('old.txt', 'w') as o:
        o.write(str(n))
    log('No more old posts left!' if n >= lim else 'Old posts processed.')


def main():
    confession = Thread(target=preacher)
    confession.start()
    log(datetime.now().strftime(r"Start @ %H:%M:%S MSC"))
    new = safeguard(target=do_new, retries=3)
    if not new[0]:
        message = 'A problem occurred when trying to process new posts:\n\n{}\n\n'.format(new[1])
        log(message)
        with open('TRACEBACK_NEW.TXT', 'a' if 'TRACEBACK_NEW.TXT' in listdir(getcwd()) else 'w') as o:
            o.write(message)
    old = safeguard(target=do_old, retries=3)
    if not old[0]:
        message = 'A problem occurred when trying to process old posts:\n\n{}\n\n'.format(old[1])
        log(message)
        with open('TRACEBACK_OLD.TXT', 'a' if 'TRACEBACK_OLD.TXT' in listdir(getcwd()) else 'w') as o:
            o.write(message)
    log(datetime.now().strftime(r"End @ %H:%M:%S MSC"))
    praying_queue.put(None)
    confession.join(timeout=300)
    print('Praying done.\n\n')


if 'impdro' not in listdir(getcwd()):
    mkdir('impdro')
chdir('impdro')
praying_queue = Queue()
next_call = ((hour() + 1) // 2 * 2 + 1) % 24
while True:
    a = Thread(target=main)
    a.start()
    while hour() != next_call:
        sleep(300)
    next_call += 2
    next_call %= 24
