#!/usr/bin/env python3
from os import chdir, mkdir
from os.path import exists
from threading import Thread
from time import sleep
from typing import Tuple, Final

from PIL import Image, ImageOps, ImageFont
from pydub import AudioSegment

from SKTools import Logger, safeguard, altdiv, RetriesLog
from SKTools.booru import Booru
from SKTools.files import remove_file, change_extension
from SKTools.images import extended_by, vertical_merge, draw_text_with_wrap, extended_to, draw_line_no_wrap, crop_bg, \
    horizontal_merge
from SKTools.links import github_repository_link
from SKTools.tg import Bot, reply_dict, get_langcode, nice_username, unwrap_update, nice_chat_name, \
    get_chat_id_and_user_id, \
    html_user_mention_with_nice_username
from SKTools.tokens import beta_lupi_token as bot_token, preaching_room_id, olive
from SKTools.vk import Reposter
from betalupi.localizations import strings, get_help_text, interpolation_methods, max_image_size

font_name: Final = 'times.ttf'  # todo: a font for emoji, Chinese, Japanese, etc.


def docced(*commands: str) -> Tuple[str, ...]:
    return commands + tuple(f'{command}doc' for command in commands)


help_commands = 'start', 'help', 'help_extended', 'help_tags', 'help_demotivator', 'help_sticker'
shrug_commands = 'shrug',
mspabooru_commands = 'mspabooru', 'mspaboorudoc', 'mspadoc'
mspabooru_count_commands = 'mspaboorucount', 'mspacount'
olive_commands = 'olive',
compression_commands = 'jpeg', 'jpg', 'compress', 'compression'
mp3_commands = 'mp3',
demotivator_commands = docced('demotivator', 'dem', 'd')
quote_commands = docced('quote', 'qt', 'q')
sticker_commands = 'resize', 'sticker'
coordinates_commands = docced('coordinates', 'political_coordinates', 'pc', 'coord', 'pol')
converter_commands = *compression_commands, *mp3_commands, *demotivator_commands, *quote_commands, *sticker_commands, \
                     *coordinates_commands
github_commands = 'github',


def get_profile_picture(user: dict, profile_picture_side_size: int = 640) -> str:
    if profile_pictures := bot.method('getUserProfilePhotos', user_id=user['id'], limit=1)['photos']:
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


def make_quote(message: dict) -> (False, str):
    if 'reply_to_message' not in message:
        return False
    if (text := ((quoted := message['reply_to_message']).get('text') or quoted.get('caption'))) is None:
        return False
    else:
        text = text[:1024]
    start_size = 640
    file_name = get_profile_picture(user := (quoted.get('forward_from') or quoted['from']), start_size)
    img = Image.open(file_name)
    img = extended_by(img, *(altdiv(start_size, 16),) * 4, 'white')  # todo: coloUr

    text = draw_text_with_wrap(f'“{text}”', ImageFont.truetype(font_name, altdiv(start_size, 5)), start_size * 2)
    username = draw_text_with_wrap(f'© {nice_username(user, include_username=True)}',
                                   ImageFont.truetype(font_name, altdiv(start_size, 8)),
                                   max_width=start_size * 3, text_color=(128,) * 3)
    # todo: adaptive font sizes
    #   and adaptive sizes overall
    border = altdiv(start_size, 16)
    text = vertical_merge(text, username, align='right' if text.size[0] > username.size[0] else 'center',
                          interval=border)
    img = horizontal_merge(img, crop_bg(text), interval=border * 2)
    extended_by(img, *(border * 4,) * 4).save(file_name)
    return file_name


def make_demotivator(message: dict) -> (False, str):
    if not (file_name := bot.extract_and_download_photo(message, max_doc_size=max_image_size)):
        if 'reply_to_message' in message:
            file_name = make_quote(message) or get_profile_picture(message['reply_to_message']['from'])
        else:
            return False
    caption = message['text'][:1024].split('\n')
    caption = (' '.join(caption[0].split()[1:]), '\n'.join(caption[1:]))
    img = Image.open(file_name)
    w, h = img.size
    border = altdiv(w + h, 200)
    side_padding = altdiv(w, 12)  # todo: swap it with above_padding if image is vertical
    above_padding = altdiv(h, 12)
    below_padding = altdiv(h, 42)
    img = ImageOps.expand(ImageOps.expand(img, border=border, fill='black'), border=border, fill='white')
    img = extended_by(img, above_padding, side_padding, side_padding, below_padding)
    max_width = img.size[0] - side_padding
    top_font = ImageFont.truetype(font_name, altdiv(w, 7))
    bottom_font = ImageFont.truetype(font_name, altdiv(w, 14))
    img = vertical_merge(img, draw_text_with_wrap(caption[0], top_font, max_width),
                         Image.new('RGBA', (1, below_padding)),
                         draw_text_with_wrap(caption[1], bottom_font, max_width))
    extended_by(img, bottom=below_padding * 5).save(file_name)
    return file_name


def compress_photo(message: dict) -> (False, str):
    if not (file_name := bot.extract_and_download_photo(message, max_doc_size=max_image_size)):
        return False
    quality = message['text'].split(' ')
    quality = quality[1] if len(quality) > 1 else 0
    try:
        quality = int(quality)
    except ValueError:
        quality = 0
    quality = (11 - quality) if 1 <= quality <= 10 else 5
    Image.open(file_name).save(file_name, optimize=True, quality=quality)
    return file_name


def convert_voice(message: dict) -> (False, str):
    if (old_file_name := bot.extract_and_download_voice(message)) is None:
        return False
    new_file_name = change_extension(old_file_name, 'mp3')
    AudioSegment.from_file(old_file_name).export(new_file_name, format='mp3')
    remove_file(old_file_name)
    return new_file_name


def resize_to_sticker(message: dict) -> (False, str):
    if not (file_name := bot.extract_and_download_photo(message, max_doc_size=max_image_size)):
        return False
    methods = dict((method_name, eval(f'Image.{method_name}')) for method_name in interpolation_methods)
    method_name = message['text'].split()
    if len(method_name) < 2 or (method_name := method_name[1].upper()) not in methods:
        method_name = 'BICUBIC'
    img = Image.open(file_name)  # todo: RGBA
    w, h = img.size
    w, h = (512, round(512 * h / w)) if w >= h else (round(512 * w / h), 512)
    new_file_name = change_extension(file_name, 'png')
    img.resize(size=(w, h), resample=methods[method_name]).save(new_file_name)
    remove_file(file_name)
    return new_file_name


def political_coordinates(message: dict) -> (False, str):
    if not (file_name := bot.extract_and_download_photo(message, max_doc_size=max_image_size)):
        return False
    pc = Image.open('pc.png')
    # todo: overlaying
    return file_name


@safeguard(2, True)
def converter(message: dict, command: str) -> RetriesLog:
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
        raise Exception(f'{command} should not be in converter_commands')

    reply = reply_dict(message)
    if file_name:
        if command == 'mp3':
            media_type = 'Audio'
        elif 'doc' in command or command in sticker_commands:
            media_type = 'Document'
        else:
            w, h = Image.open(file_name).size
            media_type = 'Document' if w >= h * 3 or h >= w * 3 else 'Photo'
        sent = bot.method(f'send{media_type}', file_path=file_name, file_type=media_type.lower(), **reply)
        remove_file(file_name)
    else:
        sent = bot.sendMessage(f'Reply with this command to a {media} you want to {action}.', **reply)
    logger.log(sent, send=False)


def process_message(upd: dict) -> None:
    msg = unwrap_update(upd)
    if 'caption' in msg:
        msg['text'] = msg['caption']
    if 'text' in msg:
        reply = reply_dict(msg)
        langcode = get_langcode(msg)
        chat_id_user_id = get_chat_id_and_user_id(msg)
        if 'TTL' not in msg:
            msg['TTL'] = 7
        if not msg['TTL']:
            bot.sendMessage(f'Error occurred, please, contact {strings(langcode).creator}', **reply)
        else:
            msg['TTL'] -= 1
            if (command := bot.get_command(msg['text'])) in help_commands:
                bot.sendMessage(get_help_text(command, langcode), **reply,
                                parse_mode='HTML', disable_web_page_preview=True)
                chat_name = nice_chat_name(bot.chat_cache[chat_id_user_id['chat_id']])
                user_name = html_user_mention_with_nice_username(bot.user_cache[chat_id_user_id['user_id']])
                logger.log(f'Help was requested by {user_name} in <i>{chat_name}</i>', tg_params={'parse_mode': 'HTML'})
            elif command in shrug_commands:
                bot.sendMessage(strings().shrug(), **reply)
            elif command in mspabooru_commands:
                mspabooru.process_search_query_from_telegram(bot, msg, 'doc' in command)
            elif command in mspabooru_count_commands:
                mspabooru.count_for_telegram(bot, msg)
            elif command in olive_commands:
                olive_reposter.do(**reply, number_of_new_posts_to_check=0)
            elif command in converter_commands:  # todo: localization
                res = converter(msg, command)
                if not res.success:
                    logger.log(res)
                    Thread(target=process_message, args=(msg,)).start()
            elif command in github_commands:
                bot.sendMessage(github_repository_link, **reply, disable_web_page_preview=True)
            t = msg['text'].lower()
            if 'слава украине' in t or 'слава україні' in t:
                bot.sendMessage('Героям слава!', **reply)


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
    dirname = 'betalupi'
    if not exists(dirname):
        mkdir(dirname)
    chdir(dirname)

    bot = Bot(bot_token)
    bot.set_window_name()
    logger = Logger(bot, preaching_room_id)
    olive_reposter = Reposter(bot, olive, logger)
    mspabooru = Booru('mspabooru.com')

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

    olive_reposter.join()
    logger.join()
