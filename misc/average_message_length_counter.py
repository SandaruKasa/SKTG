#!/usr/bin/env python3
from json import load, dumps
from typing import Union

from SKTools import Logger, recursive_applier
from SKTools.tg import Bot, html_encode


def text_length(s: Union[dict, list, tuple, str]) -> int:
    if isinstance(s, (list, tuple)):
        return sum(map(text_length, s))
    elif isinstance(s, dict):
        return text_length(s['text'])
    elif isinstance(s, str):
        return len(s.split()) if s else 0
    else:
        raise TypeError(type(s))


input("Export chat's history (only chat's) using Telegram desktop (attachments aren't required) in JSON format, \
find result.json in the exported files, copy it to this program's directory, rename it to chat.json, \
and press Enter.\n")

messages = load(open('chat.json', encoding='utf-8'))['messages']
results = {}
for m in messages:
    if m['type'] == 'message' and 'from_id' in m:
        try:
            length = text_length(m)
            if (i := m['from_id']) in results:
                results[i]['messages'] += 1 if length else 0
                results[i]['words'] += length
            else:
                results[i] = {'name': m['from'], 'first_message_id': m['id'], 'messages': 1 if length else 0,
                              'words': text_length(m)}
        except Exception as e:
            print(m)
            raise e
results = [{'id': i, **results[i]} for i in results]
for a in results:
    if not a['name']:
        a['name'] = ''
    a['average'] = a['words'] / a['messages'] if a['messages'] else 0
results.sort(key=lambda x: x['average'], reverse=True)
with open('results.json', 'w', encoding='utf-8') as o:
    o.write(dumps(results, ensure_ascii=False, indent=4))

input("The results without ranking have been written into a newly created results.json file. You can open it \
and remove users that you don't want to include into the final leader board (for example, bots). Then save it \
and press enter here.\n")

data = recursive_applier([{'no': i[0] + 1, **i[1]} for i in enumerate(load(open('results.json', encoding='utf-8')))],
                         lambda x: html_encode(x) if x else '<i>???</i>', str)
template = '{no}. <a href="http://t.me/c/{chat_id}/{first_message_id}">{name}</a> {average:.3f} ({words} / {messages})'
greeting = f'''I have just calculated the average number of words per message for every member of this chat.
What you see below is the leader board. The format is as follows:

[Place]. [Name*] [Average**] ([words total] / [non-wordless messages total])

* If the name is missing (for example, deleted account), it is replaced with "<i>???</i>.
Each name has a link to the first message from the user.
** Messages without any words (for example, photos with no caption) don't affect the average.
If there were 0 messages with words from the user, the average is set to 0 as well.'''

bot_token = input("Now give me a token of the bot that will publish the results:\n>>> ")
chat_id = input("And now the id of the chat (I would have automated this \
if Telegram would include proper chat id into the exported history)\n>>> ")
chat_id = int(chat_id if chat_id.startswith('-100') else f'-100{chat_id}')

logger = Logger()
bot = Bot(bot_token)
results = list(map(lambda user: template.format(**user, chat_id=str(chat_id)[4:]), data))

i, j = 0, 1
parts = []
while j <= len(results):
    if j == len(results) or len('\n'.join(results[i:j + 1])) > 4096:
        parts.append('\n'.join(results[i:j]))
        i, j = j, j + 1
    else:
        j += 1
for t in [greeting] + parts:
    logger.log(bot.method('sendMessage', chat_id=chat_id, text=t, parse_mode='HTML'))
