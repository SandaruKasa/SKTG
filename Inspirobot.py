#!/usr/bin/env python3
from os import chdir, mkdir
from os.path import exists
from threading import Thread
from time import sleep

from requests import get

from SKTools import Logger
from SKTools.links import github_repository_link, inspirobot_api
from SKTools.tg import Bot, reply_dict, get_langcode, unwrap_update, nice_chat_name, \
    get_chat_id_and_user_id, \
    html_user_mention_with_nice_username
from SKTools.tokens import inspirobot_token as bot_token, preaching_room_id
from inspirobot.localizations import strings

help_commands = 'start', 'help'
send_commands = 'inspire',
github_commands = 'github',


def process_message(upd: dict) -> None:
    msg = unwrap_update(upd)
    if 'caption' in msg:
        msg['text'] = msg['caption']
    if 'text' in msg:
        reply = reply_dict(msg)
        lang = strings(get_langcode(msg))
        chat_id_user_id = get_chat_id_and_user_id(msg)

        if (command := bot.get_command(msg['text'])) in help_commands:
            bot.sendMessage(lang.help(), **reply, parse_mode='HTML', disable_web_page_preview=True)
            chat_name = nice_chat_name(bot.chat_cache[chat_id_user_id['chat_id']])
            user_name = html_user_mention_with_nice_username(bot.user_cache[chat_id_user_id['user_id']])
            logger.log(f'Help was requested by {user_name} in <i>{chat_name}</i>', tg_params={'parse_mode': 'HTML'})
        elif command in send_commands:
            image_url = get(inspirobot_api).text
            bot.sendPhoto(photo=image_url, caption=f'https://inspirobot.me/share?iuid=a/{image_url.split("/")[-1]}',
                          **reply)
        elif command in github_commands:
            bot.sendMessage(github_repository_link, **reply, disable_web_page_preview=True)


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
    dirname = 'inspirobot'
    if not exists(dirname):
        mkdir(dirname)
    chdir(dirname)

    bot = Bot(bot_token)
    bot.set_window_name()
    logger = Logger(bot, preaching_room_id)

    n = 0
    keep_running = True
    Thread(target=stopper).start()

    while keep_running:
        a = bot.get_and_process_updates(offset=n, logger=logger)
        if a.success:
            n, updates = a.result
            for u in updates:
                Thread(target=process_update, args=(u,)).start()
        else:
            print(a)
        sleep(1)

    logger.join()
