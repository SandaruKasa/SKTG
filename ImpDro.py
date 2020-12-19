from datetime import datetime
from json import dumps
from os import listdir, getcwd, chdir, mkdir
from re import sub
from threading import Thread
from time import sleep

from requests import get as r_get, post as r_post

from links import telegram_bot_api, vk_api, proxies
from tokens import imperial_drone_token, preaching_room_id, target_chat_id, original_group_id, vk_params
from tools import Logger, safeguard

bot = telegram_bot_api.format(imperial_drone_token)


@safeguard()
def safe_bot(method, **params):
    return r_post(bot + method, params=params, proxies=proxies)


@safeguard()
def safe_vk(method, **params):
    params.update(vk_params)
    return r_get(vk_api + method, params=params)


def hour():
    return datetime.now().hour


def post_post(link, text, photos, time):
    text = sub(r'\[([^|]*)\|([^]]*)\]', r'<a href="https://vk.com/\1">\2</a>', text) + \
           '\n______\n{}\n{}'.format(link, datetime.utcfromtimestamp(time).strftime(r'%Y-%m-%d @ %H:%M UTC'))
    if len(photos) == 0:
        posting_result = safe_bot('sendMessage', chat_id=target_chat_id, caption=text, parse_mode='HTML')
    elif len(photos) == 1:
        posting_result = safe_bot('sendPhoto', chat_id=target_chat_id, caption=text, parse_mode='HTML', photo=photos[0])
    else:
        media = [{'type': 'photo', 'media': photo} for photo in photos]
        media[0]['caption'] = text
        media[0]['parse_mode'] = 'HTML'
        posting_result = safe_bot('sendMediaGroup', chat_id=target_chat_id, media=dumps(media))
    logger.log(dumps(posting_result.json(), indent=1), include_time=False)


def parse_post(post):
    n = post['id']
    link = 'https://vk.com/wall{}_{}'.format(original_group_id, n)
    logger.log('Parsing {}'.format(link))
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
    posts = safe_vk('wall.get', owner_id=original_group_id, count=16).json()['response']['items']
    posts.sort(key=lambda post: post['id'])
    i = 0
    while i < len(posts) and posts[i]['id'] <= last_post_no:
        i += 1
    logger.log('Previous: {}.\n\nFresh: {}.'.format((', '.join(str(post['id']) for post in posts[:i]) if i else 'none'),
                                                    (', '.join(str(post['id']) for post in posts[i:]) if i != len(
                                                        posts) else 'none')))
    for post in posts[i:]:
        last_post_no = parse_post(post)
    return last_post_no


def check_old(num):
    post = safe_vk('wall.getById', posts='{}_{}'.format(original_group_id, num)).json()
    if 'response' in post.keys() and isinstance(post['response'], list) and post['response'] \
            and post['response'][0]['from_id'] == original_group_id:
        parse_post(post['response'][0])
        return True
    else:
        traceback = 'https://vk.com/wall{}_{} #was_not_processed. Contents:\n\n{}'.format(original_group_id, num,
                                                                                          dumps(post, indent=4))
        logger.log(traceback)
        with open('{}.txt'.format(num), 'w', encoding='utf-8') as o:
            o.write(traceback)
        return False


@safeguard(3, True)
def do_new():
    logger.log('Checking for new...')
    if 'new.txt' in listdir(getcwd()):
        with open('new.txt') as o:
            n = int(o.read().strip())
    else:
        n = 0
    n = check_new(n)
    with open('new.txt', 'w') as o:
        o.write(str(n))
    logger.log('New posts processed.')


@safeguard(3, True)
def do_old():
    lim = 19395
    logger.log('Searching for old...')
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
    logger.log('No more old posts left!' if n >= lim else 'Old posts processed.')


def main():
    logger.start()
    logger.log('Start')
    new = do_new()
    if not new[0]:
        message = 'A problem occurred when trying to process new posts:\n\n{}\n\n'.format(new[1])
        logger.log(message)
        with open('TRACEBACK_NEW.TXT', 'a' if 'TRACEBACK_NEW.TXT' in listdir(getcwd()) else 'w') as o:
            o.write(message)
    old = do_old()
    if not old[0]:
        message = 'A problem occurred when trying to process old posts:\n\n{}\n\n'.format(old[1])
        logger.log(message)
        with open('TRACEBACK_OLD.TXT', 'a' if 'TRACEBACK_OLD.TXT' in listdir(getcwd()) else 'w') as o:
            o.write(message)
    logger.log('End')
    logger.stop()
    logger.join(timeout=300)
    print('Logging done.\n\n')


if 'impdro' not in listdir(getcwd()):
    mkdir('impdro')
chdir('impdro')
logger = Logger(imperial_drone_token, preaching_room_id)
next_call = ((hour() + 1) // 2 * 2 + 1) % 24
while True:
    a = Thread(target=main)
    a.start()
    while hour() != next_call:
        sleep(300)
    next_call += 2
    next_call %= 24
