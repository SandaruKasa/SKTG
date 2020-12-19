from datetime import datetime
from os import listdir, getcwd, chdir, mkdir
from time import sleep

from SKTools import Logger, safeguard
from SKTools.links import github_repository
from SKTools.tg import Bot
from SKTools.tokens import imperial_drone_token, preaching_room_id, bucket, impdro_invitation, boring_chats, impdrochats
from SKTools.vk import Reposter

greeting = f'''Hello! I am Imperial Drone bot. I was made by @SandaruKasa and here's what I can do:

/start or /help — display this message
/send_now — sends a post immediately

<a href="{github_repository}">My source code is available on GitHub</a>.'''


def hour():
    return datetime.now().hour


@safeguard(1, True)
def update(offset=0):
    updates = bot.get_updates(offset)
    logger.log(f'Updates for {bot.username} received', sep=' ', send=False)
    for upd in updates:
        offset = upd['update_id']
        try:
            k = list(upd.keys())
            k.remove('update_id')
            f = upd[k[0]]['chat']['id'] not in boring_chats
        except KeyError:
            f = True
        except ValueError:
            f = True
        logger.log(upd, send=f)
        if 'message' in upd and 'text' in upd['message']:
            upd = upd['message']
            i = upd['message_id']
            if (chat := upd['chat']['id']) in impdrochats:
                if (command := bot.get_command(upd['text'])).startswith('send'):
                    reposter.do(chat, i, False)
                elif command in ('start', 'help'):
                    logger.log(bot.method('sendMessage', chat_id=chat, text=greeting, parse_mode='HTML',
                                          reply_to_message_id=i, disable_web_page_preview=True))
            elif bot.get_command(upd['text']):
                logger.log(bot.method('sendMessage', chat_id=chat, text=impdro_invitation, reply_to_message_id=i,
                                      parse_mode='HTML', disable_web_page_preview=True))
    return offset + 1 if updates else offset


next_call = ((hour() + 1) // 2 * 2 + 1) % 24
if __name__ == '__main__':
    dirname = 'impdro'
    if dirname not in listdir(getcwd()):
        mkdir(dirname)
    chdir(dirname)
    bot = Bot(imperial_drone_token)
    logger = Logger(bot, preaching_room_id)
    logger.start()
    reposter = Reposter(bot, bucket, logger)
    sleep(1)
    n = 0
    while True:
        a = update(n)
        if a[0]:
            n = a[1]
        else:
            print(a[1])
        if hour() == next_call:
            logger.log('Starting regular check')
            for c in impdrochats:
                reposter.do(c)
            next_call += 2
            next_call %= 24
        sleep(1)
