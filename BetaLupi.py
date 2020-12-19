import xml.etree.ElementTree as ETree
from os import listdir, getcwd, chdir, mkdir
from queue import Queue
from random import randint
from re import sub
from threading import Thread
from time import sleep
from urllib.parse import quote

from PIL import Image, ImageOps, ImageFont
from pydub import AudioSegment

from SKTools import Logger, safeguard, altdiv, remove_file
from SKTools.images import extended_by, vertical_merge, draw_text_with_wrap, extended_to, draw_line_no_wrap, crop_bg, \
    horizontal_merge
from SKTools.links import telegram_bot_api, github_repository
from SKTools.proxies import proxy_request as request
from SKTools.tg import Bot, reply_dict, extract_media
from SKTools.tokens import beta_lupi_token as bot_token, preaching_room_id, boring_chats, me, olive
from SKTools.vk import Reposter

bot = telegram_bot_api.format(bot_token)
shrug = r'¯\_(ツ)_/¯'
greeting = f'''Hello! I am Beta Lupi bot, but you can call me Kekouan.
I was made by @SandaruKasa and here's what I can do:

/start or /help — displays this message
/shrug — sends a {shrug}
/jpeg [compression level] — reply with this to a picture you want to compress. Level should be an integer, 1 &lt;= \
level &lt;= 10 (the greater the level is, the more compression you get). Default level is 6. \
(/jpg, /compress, or /compression work too)
/mspabooru [tags] — sends a random artwork with given tags from mspabooru.com 
/mspadoc [tags] — same as above but via a document
/gelbooru [tags] — sends a random artwork with given tags from gelbooru.com (may be NSFW)
/geldoc [tags] — same as above but via a document (may be NSFW) 
/olive — sends a Leijon from <a href="https://vk.com/nepetafans">a VK group</a>.
/mp3 — reply with this to a voice message you want to convert to a .mp3 file

<a href="{github_repository}">My source code is available on GitHub</a>.'''
tasks = Queue()
ttl_error_message = '''I made several attempts to do what you asked, but I couldn't...
3:
Please, tell @SandaruKasa about what happened.'''  # todo: languages
# todo: update with new commands
font_name = 'times.ttf'  # todo: a font for emoji, Chinese, Japanese, etc.


def docced(*commands):
    return commands + tuple(f'{command}doc' for command in commands)


compression_commands = 'jpeg', 'jpg', 'compress', 'compression'
mp3_commands = 'mp3',
demotivator_commands = docced('demotivator', 'dem', 'd')
quote_commands = docced('quote', 'qt', 'q')
sticker_commands = 'resize', 'sticker'
coordinates_commands = docced('coordinates', 'political_coordinates', 'pc', 'coord', 'pol')
converter_commands = *compression_commands, *mp3_commands, *demotivator_commands, *quote_commands, *sticker_commands, \
                     *coordinates_commands


def booru(message, booru_name, doc_requested=False):
    booru_api = 'https://' + booru_name + '/index.php?page=dapi&s=post&q=index&limit={}&tags={}&pid={}'

    @safeguard(4, True)
    def booru_core(m):
        reply = {'chat_id': m['chat']['id'], 'reply_to_message_id': m['message_id']}
        tags = quote(sub(r'/[^ ]*', '', m['text']).strip())
        ignore_proxies = 'mspa' in booru_name
        total = int(
            ETree.fromstring(request(booru_api.format(0, tags, 0), ignore_proxies=ignore_proxies).text).attrib['count'])
        if total:
            offset = randint(0, min(20000, total - 1))
            post = ETree.fromstring(request(booru_api.format(1, tags, offset), ignore_proxies=ignore_proxies).text)[
                0].attrib
            caption = f'Taken from: https://{booru_name}/index.php?page=post&s=view&id={post["id"]}'
            url = post['file_url']
            logger.log(url)
            name = url.split('/')[-1]
            extension = name.split('.')[-1]
            if not doc_requested and extension in ('jpg', 'jpeg', 'png') and int(post['height']) < 1920 \
                    and int(post['width']) < 1920:
                sent = bot.method('sendPhoto', photo=url, caption=caption, **reply)
            else:
                with open(name, 'wb') as out:
                    out.write(request(url, ignore_proxies=ignore_proxies).content)
                sent = bot.method('sendDocument', file=open(name, 'rb'), caption=caption, **reply)
                remove_file(name)
        else:
            sent = bot.method('sendMessage', text="I didn't find anything...", **reply)
        logger.log(sent)
        return sent and sent['ok']

    res = booru_core(message)
    if not res[0] or not res[1]:
        print(res[1])
        tasks.put({'message': message})


def get_profile_picture(user: dict, profile_picture_side_size=640):
    if profile_pictures := bot.method('getUserProfilePhotos', user_id=user['id'],
                                      limit=1)['result']['photos']:
        file_name = bot.download_photo(profile_pictures[0], resolution_picker=lambda x: min(x, key=lambda r: abs(
            profile_picture_side_size - r['width'])))
        img = Image.open(file_name)
        if img.size[0] != profile_picture_side_size:
            img = img.resize((profile_picture_side_size,) * 2)
    else:
        file_name = f'{user["id"]}.png'
        initials = user['first_name'][0]
        initials += user.get('last_name', [''])[0]
        # todo: coloUrs
        img = draw_line_no_wrap(initials, ImageFont.truetype(font_name, altdiv(2 * profile_picture_side_size, 3)))
        img = extended_to(crop_bg(img), profile_picture_side_size, profile_picture_side_size)
    img.save(file_name)
    return file_name


def make_quote(message):
    if 'reply_to_message' not in message:
        return False
    if (text := (quoted := message['reply_to_message']).get('text', None) or quoted.get('caption', None)) is None:
        return False
    start_size = 640
    file_name = get_profile_picture(user := (quoted.get('forward_from', None) or quoted['from']), start_size)
    img = Image.open(file_name)
    img = extended_by(img, *(altdiv(start_size, 16),) * 4, 'white')  # todo: coloUr
    username = f'{user["first_name"]} '
    if 'username' in user:
        username += f'“{user["username"]}” '
    username += user.get('last_name', '')

    text = draw_text_with_wrap(f'“{text}”', ImageFont.truetype(font_name, altdiv(start_size, 5)), start_size * 2)
    username = draw_text_with_wrap(f'© {username}', ImageFont.truetype(font_name, altdiv(start_size, 8)),
                                   max_width=start_size * 3, text_color=(128,) * 3)
    # todo: adaptive font sizes
    #   and adaptive sizes overall
    border = altdiv(start_size, 16)
    text = vertical_merge(text, username, align='right' if text.size[0] > username.size[0] else 'center',
                          interval=border)
    img = horizontal_merge(img, crop_bg(text), interval=border * 2)
    extended_by(img, *(border * 4,) * 4).save(file_name)
    return file_name


def make_demotivator(message):
    if (photo := extract_media(message, 'photo')) is not None:
        file_name = bot.download_photo(photo)
    elif 'reply_to_message' in message:
        file_name = make_quote(message) or get_profile_picture(message['reply_to_message']['from'])
    else:
        return False
    caption = message['text'].split('\n')
    caption = (' '.join(caption[0].split()[1:]), '\n'.join(caption[1:]))
    img = Image.open(file_name)
    w, h = img.size
    border = altdiv(w + h, 200)
    side_padding = altdiv(w, 12)
    above_padding = altdiv(h, 12)
    below_padding = altdiv(h, 42)
    img = ImageOps.expand(ImageOps.expand(img, border=border, fill='black'), border=border, fill='white')
    img = extended_by(img, above_padding, side_padding, side_padding, below_padding)
    max_width = img.size[0] - side_padding
    top_font = ImageFont.truetype(font_name, altdiv(w, 6))
    bottom_font = ImageFont.truetype(font_name, altdiv(w, 16))
    img = vertical_merge(img, draw_text_with_wrap(caption[0], top_font, max_width),
                         Image.new('RGB', (1, below_padding)),
                         draw_text_with_wrap(caption[1], bottom_font, max_width))
    extended_by(img, bottom=below_padding * 3).save(file_name)
    return file_name


def compress_photo(message):
    if (photo := extract_media(message, 'photo')) is None:
        return False
    file_name = bot.download_photo(photo)
    quality = message['text'].split(' ')
    quality = quality[1] if len(quality) > 1 else 0
    try:
        quality = int(quality)
    except ValueError:
        quality = 0
    quality = (11 - quality) if 1 <= quality <= 10 else 5
    Image.open(file_name).save(file_name, optimize=True, quality=quality)
    return file_name


def convert_voice(message):
    if (voice := extract_media(message, 'voice')) is None:
        return False
    old_file_name = bot.download_file(voice['file_id'])
    new_file_name = f'{".".join(old_file_name.split(".")[:-1])}.mp3'
    AudioSegment.from_file(old_file_name).export(new_file_name, format='mp3')
    remove_file(old_file_name)
    return new_file_name


def resize_to_sticker(message):
    if (photo := extract_media(message, 'photo')) is None:  # todo: doc support
        return False
    methods = dict((resampling_filter, eval(f'Image.{resampling_filter}')) for resampling_filter in
                   ('NEAREST', 'BOX', 'BILINEAR', 'HAMMING', 'BICUBIC', 'LANCZOS'))
    method_name = message['text'].split()
    if len(method_name) < 2 or (method_name := method_name[1].upper()) not in methods:
        method_name = 'BICUBIC'
    file_name = bot.download_photo(photo, file_name_salt=method_name)
    img = Image.open(file_name)
    w, h = img.size
    w, h = (512, round(512 * h / w)) if w >= h else (round(512 * w / h), 512)
    img.resize(size=(w, h), resample=methods[method_name]).save(file_name)
    return file_name


def political_coordinates(message):
    if (photo := extract_media(message, 'photo')) is None:
        return False
    file_name = bot.download_photo(photo)
    pc = Image.open('pc.png')
    # todo: overlaying
    return file_name


def converter(message, command):
    if command in quote_commands:
        media, action = 'message', 'make a quote out of'
        file_name = make_quote(message)
    elif command in mp3_commands:
        media, action = 'voice message', 'convert to mp3'
        file_name = convert_voice(message)
    elif command in demotivator_commands:
        media, action = 'message or a photo', 'make a demotivator out of'
        file_name = make_demotivator(message)
    elif command in compression_commands:
        media, action = 'photo', 'compress'
        file_name = compress_photo(message)
    elif command in sticker_commands:
        media, action = 'photo', 'resize for a sticker'
        file_name = resize_to_sticker(message)
    elif command in coordinates_commands:
        media, action = 'photo', 'overlay political coordinates on'
        file_name = political_coordinates(message)
    else:
        bot.method('sendMessage', chat_id=me, text=f'Your converter accepts {command} but can\'t process it.')
        return

    reply = reply_dict(message)
    if file_name:
        if command == 'mp3':
            media_type = 'Audio'
        elif 'doc' in command or command in sticker_commands:
            media_type = 'Document'
        else:
            w, h = Image.open(file_name).size
            media_type = 'Document' if w >= h * 3 or h >= w * 3 else 'Photo'
        sent = bot.method(f'send{media_type}', file=open(file_name, 'rb'), file_type=media_type.lower(), **reply)
        remove_file(file_name)
    else:
        sent = bot.method('sendMessage', text=f'Reply with this command to a {media} you want to {action}.', **reply)

    if sent and sent['ok']:
        logger.log(sent, send=False)
    else:
        logger.log(message, sent)
        tasks.put({'message': message})


def processor():
    while True:
        if not tasks.empty():
            upd = tasks.get()
            if 'message' in upd.keys():
                upd = upd['message']
                if 'caption' in upd:
                    upd['text'] = upd['caption']
                if 'text' in upd:
                    if 'TTL' not in upd.keys():
                        upd['TTL'] = 7
                    if not upd['TTL']:
                        bot.method('sendMessage', **reply_dict(upd), text=ttl_error_message)
                    else:
                        upd['TTL'] -= 1
                        if (command := bot.get_command(upd['text'])) in ('start', 'help'):
                            bot.method('sendMessage', **reply_dict(upd), text=greeting, parse_mode='HTML',
                                       disable_web_page_preview=True)
                        elif command == 'shrug':
                            bot.method('sendMessage', **reply_dict(upd), text=shrug)
                        elif command in ('mspabooru', 'mspadoc', 'gelbooru', 'geldoc'):
                            Thread(target=booru, args=(upd, 'mspabooru.com' if 'mspa' in command else 'gelbooru.com',
                                                       'doc' in command)).start()
                        elif command == 'olive':
                            olive_reposter.do(upd['chat']['id'], upd['message_id'], 0)
                        elif command in converter_commands:
                            Thread(target=converter, args=(upd, command)).start()
            tasks.task_done()
        else:
            sleep(1 / 4)


@safeguard(1, True)
def update(offset=0):
    updates = bot.get_updates(offset)
    logger.log(f'Updates for {bot.username} received', sep=' ', send=False)
    for upd in updates:
        offset = upd['update_id']
        tasks.put(upd)
        try:
            k = list(upd.keys())
            k.remove('update_id')
            f = upd[k[0]]['chat']['id'] not in boring_chats
        except KeyError:
            f = True
        except ValueError:
            f = True
        logger.log(upd, send=f)
    return offset + 1 if updates else offset


if __name__ == '__main__':
    dirname = 'betalupi'
    if dirname not in listdir(getcwd()):
        mkdir(dirname)
    chdir(dirname)
    bot = Bot(bot_token)
    Thread(target=processor).start()
    logger = Logger(bot, preaching_room_id, queue_sleeping_delay=2)
    logger.start()
    olive_reposter = Reposter(bot, olive, logger)
    n = 0
    while True:
        a = update(n)
        if a[0]:
            n = a[1]
        else:
            print(a[1])
        sleep(1)
