#!/usr/bin/env python3
from datetime import datetime
from json import loads, dumps
from os import chdir, mkdir, remove, listdir
from os.path import getsize, exists
from random import shuffle, randint
from threading import Thread, RLock
from time import sleep
from typing import Optional, List, Union, Tuple

from SKTools import Logger, split_into_parts
from SKTools.booru import Booru
from SKTools.files import folder_walker, sk_open, join_path, split_path, CachedSet, CachedDict
from SKTools.links import github_repository_link
from SKTools.tg import Bot, reply_dict, get_langcode, get_chat_id_and_user_id, html_user_mention_with_nice_username, \
    html_chat_name
from SKTools.tokens import imperial_drone_token, preaching_room_id, bucket, impdro_vk_blacklist, \
    impdro_database_link, database_archives, easter_egg_sticker_id
from SKTools.vk import Reposter
from impdro.localizations import strings

help_commands = 'help', 'start'
random_commands = 'random',
vk_commands = 'vk', 'bucket'
database_commands = 'db', 'database'
search_commands = 'tag', 'search', 'find'
special_commands = 'send',
database_share_commands = []
for prefix in ('get', 'send'):
    for joiner in ('', '_'):
        for suffix in database_commands:
            database_share_commands.append(f'{prefix}{joiner}{suffix}')
github_commands = 'github',
subscribe_commands = 'subscribe',
unsubscribe_commands = 'unsubscribe',
gelbooru_commands = 'gelbooru', 'gelboorudoc', 'geldoc'
gelbooru_count_commands = 'gelboorucount', 'gelcount'
counted_commands = *random_commands, *vk_commands, *database_commands, *search_commands, *special_commands
# todo: blacklisted commands
get_counter_commands = 'top',


def hour() -> int:
    return datetime.now().hour


def get_split_file_path_from_queue(chat_id: int, database_folder_name: str = 'database') -> List[str]:
    with queue_locks.setdefault(chat_id, RLock()):
        if not exists(queue_name := join_path('queue', f'{chat_id}.skdb')):
            files = list(split_path(file_name) for file_name in folder_walker(database_folder_name)
                         if getsize(file_name) <= 50_000_000 and 'Thumbs.db' not in file_name
                         and 'desktop.ini' not in file_name)
            shuffle(files)
            with sk_open(queue_name, 'w') as f:
                f.write('\n'.join(dumps(i, ensure_ascii=False) for i in files[1:]))
            result = files[0]
        else:
            with sk_open(queue_name) as o:
                result, rest = loads(o.readline().strip()), o.read()
            if rest:
                with sk_open(queue_name, 'w') as o:
                    o.write(rest)
            else:
                remove(queue_name)
    return result


def post_from_database(chat_id: int, reply_to_message_id: Optional[int] = None) -> None:
    file_path = get_split_file_path_from_queue(chat_id)
    logger.log(file_name := join_path(file_path), send=False)
    reply = {'chat_id': chat_id,
             'caption': '/'.join([f'<a href="{impdro_database_link}">{file_path[0]}</a>', *file_path[1:]])}
    if reply_to_message_id is not None:
        reply['reply_to_message_id'] = reply_to_message_id
    if file_name.split('.')[-1].lower() in ('jpg', 'jpeg', 'png') and getsize(file_name) <= 10_000_000:
        reply = reply_dict(bot.sendPhoto(file_path=file_name, **reply, parse_mode='HTML'))
    bot.sendDocument(file_path=file_name, **reply, parse_mode='HTML')


def post_random_from_vk(chat_id: int, reply_to_message_id: Optional[int] = None) -> bool:
    if chat_id in impdro_vk_blacklist:
        return False
    reply = {'chat_id': chat_id}
    if reply_to_message_id:
        reply['reply_to_message_id'] = reply_to_message_id
    reposter.do_random(reply)
    return True


def post_from_vk(chat_id: int, reply_to_message_id: Optional[int] = None) -> bool:
    if chat_id in impdro_vk_blacklist:
        return False
    elif chat_id in mailing_list:
        reposter.do(chat_id, reply_to_message_id, number_of_new_posts_to_check=0)
        return True
    else:
        post_random_from_vk(chat_id, reply_to_message_id)
        return True


def post_autoselect(chat_id: int, reply_to_message_id: Optional[int] = None) -> None:
    post_from_vk(chat_id, reply_to_message_id) if randint(0, int(chat_id not in impdro_vk_blacklist)) \
        else post_from_database(chat_id, reply_to_message_id)


def post_tag(message: dict) -> bool:
    query = ' '.join(f'#{i}' for i in message['text'].split()[1:])
    if not query:
        return False
    if (reply := reply_dict(message))['chat_id'] in impdro_vk_blacklist:
        bot.sendMessage(strings(get_langcode(message)).vk_blacklist(), **reply, parse_mode='HTML')
        return True
    elif not reposter.do_search(reply, query):
        bot.sendMessage(strings(get_langcode(message)).nothing_found(), **reply,
                        parse_mode='HTML')
    return True


ID = Union[str, int]
COUNTER_VALUE = Union[float, int]
PLACE = int
USER_STATS_TOTAL_ENTRY = CHAT_TOP_ENTRY = Tuple[PLACE, Tuple[ID, COUNTER_VALUE]]
USER_STATS_TOTAL = List[USER_STATS_TOTAL_ENTRY]
CHAT_TOP = List[CHAT_TOP_ENTRY]


class CachedCounters(dict):
    def __init__(self, directory_name: str = 'user_activity_counter'):
        self._directory_name = directory_name
        self._lock = RLock()

        def _pairer(file_name: str) -> Tuple[str, CachedDict]:
            return file_name.split('.json')[0], CachedDict(join_path(self._directory_name, file_name))

        with self._lock:
            super().__init__(map(_pairer, listdir(self._directory_name)))

    def __getitem__(self, chat_id: ID) -> CachedDict:
        chat_id = str(chat_id)
        with self._lock:
            try:
                return super().__getitem__(chat_id)
            except KeyError:
                self[chat_id] = res = CachedDict(join_path(self._directory_name, f'{chat_id}.json'))
                return res

    def increase(self, chat_id: ID, user_id: ID, increment: COUNTER_VALUE = 1) -> None:
        with self._lock:
            counter = self[chat_id]
            counter[user_id] = counter.get(user_id, 0) + increment

    def get_user_stats_total(self, user_id: ID) -> USER_STATS_TOTAL:
        with self._lock:
            res = [(chat_id, counter_value) for chat_id in self.keys() if
                   (counter_value := self[chat_id].get(user_id)) is not None]
            return list(enumerate(sorted(res, key=lambda x: x[1], reverse=True), start=1))

    def get_chat_top(self, chat_id: ID) -> CHAT_TOP:
        with self._lock:
            results = list(self[chat_id].items())
            results.sort(key=lambda entry: entry[1], reverse=True)
            return list(enumerate(results, start=1))


def format_chat_top_entry(chat_top_entry: CHAT_TOP_ENTRY) -> str:
    place, t = chat_top_entry
    user_id, t = t
    return f'{place}. {html_user_mention_with_nice_username(bot.user_cache[user_id])}: {t}'


def format_user_stats_total_entry(user_stats_total_entry: USER_STATS_TOTAL_ENTRY) -> str:
    place, t = user_stats_total_entry
    chat_id, counter_value = t
    return f'{place}. <b>{counter_value}</b> — <i>{html_chat_name(bot.chat_cache[chat_id])}</i>'


def process_message(msg: dict) -> None:
    if 'caption' in msg:
        msg['text'] = msg['caption']
    if 'text' in msg:
        reply = reply_dict(msg)
        chat_id_user_id = get_chat_id_and_user_id(msg)
        lang = strings(get_langcode(msg))
        command = bot.get_command(msg['text'])
        if command in help_commands:
            bot.sendMessage(lang.help(), **reply, parse_mode='HTML', disable_web_page_preview=True)
            chat_name = html_chat_name(bot.chat_cache[chat_id_user_id['chat_id']])
            user_name = html_user_mention_with_nice_username(bot.user_cache[chat_id_user_id['user_id']])
            logger.log(f'Help was requested by {user_name} in <i>{chat_name}</i>', tg_params={'parse_mode': 'HTML'})
        elif command in counted_commands:
            user_activity_counters.increase(**chat_id_user_id)
            if randint(1, 239) == 30:
                bot.method('sendSticker', sticker=easter_egg_sticker_id, **reply)
                chat_name = html_chat_name(bot.chat_cache[chat_id_user_id['chat_id']])
                user_name = html_user_mention_with_nice_username(bot.user_cache[chat_id_user_id['user_id']])
                logger.log(f'Easter egg for {user_name} in <i>{chat_name}</i>', tg_params={'parse_mode': 'HTML'})
            elif command in random_commands:
                if not post_random_from_vk(**reply):
                    bot.sendMessage(lang.vk_blacklist(), **reply, parse_mode='HTML')
            elif command in vk_commands:
                if not post_from_vk(**reply):
                    bot.sendMessage(lang.vk_blacklist(), **reply, parse_mode='HTML')
            elif command in database_commands:
                post_from_database(**reply)
            elif command in search_commands:
                if not post_tag(msg):
                    bot.sendMessage(lang.empty_query(), **reply, parse_mode='HTML')
            elif command in special_commands:
                if not post_tag(msg):
                    post_autoselect(**reply)
        elif command in gelbooru_commands:
            gelbooru.process_search_query_from_telegram(bot, msg, 'doc' in command)
        elif command in gelbooru_count_commands:
            gelbooru.count_for_telegram(bot, msg)
        elif command in database_share_commands:
            for database_part in database_archives:
                bot.sendDocument(document=database_part, **reply)
                reply = {'chat_id': reply['chat_id']}
        elif command in github_commands:
            bot.sendMessage(github_repository_link, **reply, disable_web_page_preview=True)
        elif command in subscribe_commands or command in unsubscribe_commands:
            cid = msg['chat']['id']
            if command in subscribe_commands:
                if cid in mailing_list:
                    bot.sendMessage(lang.already_subscribed(), **reply)
                elif bot.is_user_allowed_to_use_admin_only_features(msg):
                    mailing_list.add(cid)
                    bot.sendMessage(lang.subscribed(), **reply)
                else:
                    bot.sendMessage(lang.admins_only(), **reply)
            elif command in unsubscribe_commands:
                if cid not in mailing_list:
                    bot.sendMessage(lang.already_unsubscribed(), **reply)
                elif bot.is_user_allowed_to_use_admin_only_features(msg):
                    mailing_list.remove(cid)
                    bot.sendMessage(lang.unsubscribed(), **reply)
                else:
                    bot.sendMessage(lang.admins_only(), **reply)
        elif command in get_counter_commands:
            if msg['chat']['type'] == 'private':
                formatting_function = format_user_stats_total_entry
                results = user_activity_counters.get_user_stats_total(chat_id_user_id['user_id'])
                text_prefix = lang.user_top_header()
            else:
                formatting_function = format_chat_top_entry
                results = user_activity_counters.get_chat_top(chat_id := chat_id_user_id['chat_id'])
                text_prefix = lang.chat_top_header(html_chat_name(bot.chat_cache[chat_id]))
            if results:
                for portion in split_into_parts(results, 50):
                    text = text_prefix + '\n'.join(map(formatting_function, portion))
                    text_prefix = ''
                    reply = reply_dict(bot.sendMessageSilently(text, filler=lang.loading(), parse_mode='HTML', **reply))
            else:
                bot.sendMessage(lang.no_data_yet(), **reply)


def process_update(upd: dict) -> None:
    if 'message' in upd:
        process_message(upd['message'])


def stopper():
    global keep_running
    try:
        while input().lower() != 'q':
            pass
        keep_running = False
        print('Exiting...')
    except EOFError:
        pass


if __name__ == '__main__':
    next_call = ((hour() + 1) // 2 * 2 + 1) % 24
    queue_locks = {}

    dirname = 'impdro'
    if not exists(dirname):
        mkdir(dirname)
    chdir(dirname)

    mailing_list = CachedSet('mailing_list.json')
    user_activity_counters = CachedCounters()
    bot = Bot(imperial_drone_token)
    bot.set_window_name()
    logger = Logger(bot, preaching_room_id)
    reposter = Reposter(bot, bucket, logger)
    gelbooru = Booru('gelbooru.com')

    n = 0
    keep_running = True
    Thread(target=stopper).start()

    while keep_running:
        a = bot.get_and_process_updates(offset=n, logger=logger)
        if a.success:
            n, upds = a.result
            for u in upds:
                Thread(target=process_update, args=(u,)).start()
        else:
            print(a)
        if hour() == next_call:
            logger.log('Starting regular check', send=False)
            for mailing_list_chat_id in mailing_list:
                Thread(target=post_autoselect, args=(mailing_list_chat_id,)).start()
            next_call = (next_call + 2) % 24
        sleep(1)

    reposter.join()
    logger.join()
