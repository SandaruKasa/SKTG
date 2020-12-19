#!/usr/bin/env python3
from json import dumps
from os import system, name as os_name
from queue import Queue
from threading import Thread
from time import sleep
from typing import Optional, Container, Union, Dict, Any, List

from requests import get, post

from SKTools import safeguard, Logger, RetriesLog
from SKTools.files import CachedDict, join_path
from SKTools.links import telegram_bot_api

html_replacements = ('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'), ('"', '&quot;')


def html_encode(text: str) -> str:
    for pair in html_replacements:
        text = text.replace(*pair)
    return text


def html_decode(text: str) -> str:
    for pair in html_replacements[::-1]:
        text = text.replace(*pair[::-1])
    return text


def inline_keyboard_button(label_text: str, **params) -> dict:
    if (n := len(params)) != 1:
        raise KeyError(f'You must use exactly one optional field for an inline keyboard button. You used: {n}')
    params['text'] = label_text
    return params


def inline_keyboard(*button_rows: List[dict]) -> str:
    return dumps({'inline_keyboard': button_rows}, ensure_ascii=False)


def reply_dict(message: dict) -> dict:
    return {'chat_id': message['chat']['id'], 'reply_to_message_id': message['message_id']}


def unwrap_update(update: dict) -> dict:
    # If input is an Update object, returns an object that it contains, otherwise returns the object passed
    if 'update_id' in update:
        return update[[i for i in update if i != 'update_id'][0]]
    else:
        return update


def get_user(user_containing_object: dict) -> Optional[dict]:
    # Returns a User object from the passes object if it is an Update object or
    # an object that contains a User object and can be contained by an Update object; otherwise, None
    user_containing_object = unwrap_update(user_containing_object)
    return user_containing_object.get('from') or user_containing_object.get('user')


def get_user_id(user_or_user_containing_object: dict) -> Optional[int]:
    # If present, returns the id value from a User object or any object accepted by get_user
    return (get_user(user_or_user_containing_object) or user_or_user_containing_object).get('id')


def get_langcode(user_or_user_containing_object: dict) -> Optional[str]:
    # If present, returns the language_code value from a User object or any object accepted by get_user
    return (get_user(user_or_user_containing_object) or user_or_user_containing_object).get('language_code')


def get_chat(chat_or_chat_containing_object: dict) -> Optional[dict]:
    def get_chat_core(x: dict) -> Optional[dict]:
        return x.get('type') in ('private', 'group', 'supergroup', 'channel') and x or unwrap_update(x).get('chat')

    c = chat_or_chat_containing_object
    return get_chat_core(c) or get_chat_core(unwrap_update(c)) or get_chat_core(unwrap_update(c).get('message', {}))


def get_chat_id(chat_or_chat_containing_object: dict) -> Optional[int]:
    # Similar to get_lang, but the id from a Chat object rather than the language_code from a User object
    chat = get_chat(chat_or_chat_containing_object)
    return chat and chat.get('id')


def get_chat_id_and_user_id(message: dict) -> Dict[str, Optional[int]]:
    return {'chat_id': get_chat_id(message), 'user_id': get_user_id(message)}


def extract_media(message: dict, media_type: str) -> Optional[dict]:
    if media_type in message:
        return message[media_type]
    elif 'reply_to_message' in message and media_type in message['reply_to_message']:
        return message['reply_to_message'][media_type]
    else:
        return None


def nice_username(user: dict, opening_quotation_mark: str = '“', closing_quotation_mark: str = '”',
                  include_username: bool = False) -> str:
    res = user["first_name"]
    if include_username and 'username' in user:
        res += f' {opening_quotation_mark}{user["username"]}{closing_quotation_mark}'
    return (res + ' ' + user['last_name']) if 'last_name' in user else res


def nice_chat_name(chat: dict, opening_quotation_mark: str = '“', closing_quotation_mark: str = '”',
                   include_username: bool = False) -> str:
    return nice_username(chat, opening_quotation_mark, closing_quotation_mark, include_username) \
        if chat['type'] == 'private' else chat['title']


def html_chat_name(chat: dict, opening_quotation_mark: str = '“', closing_quotation_mark: str = '”',
                   include_username: bool = False) -> str:
    return html_encode(nice_chat_name(chat, opening_quotation_mark, closing_quotation_mark, include_username))


def html_user_mention_with_nice_username(user: dict, opening_quotation_mark: str = '“',
                                         closing_quotation_mark: str = '”', include_username: bool = False) -> str:
    return f'<a href="tg://user?id={user["id"]}">' + html_encode(nice_username(
        user, opening_quotation_mark, closing_quotation_mark, include_username)) + '</a>'


def unformat(text: str, parse_mode: Optional[str] = None) -> str:
    if parse_mode is not None:
        from re import sub, findall
        parse_mode = parse_mode.lower()
        if parse_mode == 'html':
            pattern_pairs = (r'<[^/>]*>([^<]*)</[^>]*>', r'\1'),
            from SKTools import html_replacements as replacement_pairs
        elif parse_mode == 'markdown':
            pattern_pairs = (r'[^\\]\*([^*])*', r'\1'), (r'[^\\]_([^_])*', r'\1'), \
                            (r'[^\\]```[^\n]*((?s:.)*?)```', r'\1'), (r'[^\\]`([^`])*', r'\1'), \
                            (r'[^\\]\[([^\]]*\])\([^)]*\)', r'\1')
            replacement_pairs = [(char, f'\\{char}') for char in ('_', '*', '`', '[')]
        else:  # todo: markdown v2
            pattern_pairs, replacement_pairs = (), ()
        # note that in pattern_pairs each pair is (encoded, decoded)
        # but in replacement_pairs each pair is (decoded, encoded)
        while any(findall(pair[0], text) for pair in pattern_pairs):
            for pair in pattern_pairs:
                text = sub(*pair, text)
        for pair in replacement_pairs:
            text = pair[0].join(text.split(pair[1]))
    return text


def text_length(text: str, parse_mode: Optional[str] = None) -> int:
    return len(unformat(text, parse_mode))


class CachedDictWithIDPopping(CachedDict):
    ID = Union[int, str]

    def __getitem__(self, key: ID):
        res = super().__getitem__(key)
        res['id'] = int(key)
        return res

    def __setitem__(self, key: ID, value: dict):
        try:
            value = value.copy()
            value.pop('id')
        except KeyError:
            pass
        super().__setitem__(key, value)

    def auto_add(self, value_with_id_key: dict):
        value_with_id_key = value_with_id_key.copy()
        super().__setitem__(value_with_id_key.pop('id'), value_with_id_key)


class UserCache(CachedDictWithIDPopping):
    def add(self, user_or_user_containing_object: dict) -> None:
        self.auto_add(dict(get_user(user_or_user_containing_object) or user_or_user_containing_object))


class ChatCache(CachedDictWithIDPopping):
    def get_number_of_messages(self, chat_id: int) -> int:
        return self.get(chat_id, {}).get('messages', 0)

    def add(self, chat_or_chat_containing_object: dict) -> None:
        chat = get_chat(chat_or_chat_containing_object)
        if chat is not None:
            c = chat.copy()
            c['messages'] = self.get_number_of_messages(chat['id']) + 1
            self.auto_add(c)


class Bot:
    def __init__(self, token: str,
                 minimal_number_of_messages_to_consider_a_chat_not_worth_logging_to_telegram: int = 7,
                 user_cache_name: Optional[str] = 'user_cache.json',
                 chat_cache_name: Optional[str] = 'chat_cache.json',
                 use_subdirectory_for_caches: bool = True, subdirectory_name: Optional[str] = None):
        self.token = token
        self.api_link = telegram_bot_api.format(self.token)
        self.me = self.method('getMe')
        self.username = self.me['username']
        self.mnomtacnwltt = minimal_number_of_messages_to_consider_a_chat_not_worth_logging_to_telegram
        if use_subdirectory_for_caches and (subdirectory_name is None):
            subdirectory_name = f'bot_{self.me["id"]}_cache'
        self.user_cache = None if user_cache_name is None else \
            UserCache(join_path(subdirectory_name, user_cache_name) if use_subdirectory_for_caches else user_cache_name)
        self.chat_cache = None if chat_cache_name is None else \
            ChatCache(join_path(subdirectory_name, chat_cache_name) if use_subdirectory_for_caches else chat_cache_name)

    @safeguard(2)
    def method(self, method: str, file_path: Optional[str] = None, file_type: str = 'document', **params) \
            -> Union[dict, list, bool, str, int, float, None]:
        def method_core(method_name: str, request_kwargs: Dict[str, Any]) -> dict:
            r = post(self.api_link + method_name, **request_kwargs).json()
            while r.get('error_code') == 429:
                sleep(r['parameters']['retry_after'] + 1)
                r = post(self.api_link + method_name, **request_kwargs).json()
            return r

        kwargs = {'params': params}
        if file_path is not None:
            kwargs['files'] = {file_type: open(file_path, 'rb')}
        res = method_core(method, kwargs)
        if res.get('description') == 'Bad Request: reply message not found':
            kwargs['params'].pop('reply_to_message_id')
            res = method_core(method, kwargs)
        if res.get('description') in ('Bad Request: message is too long', 'Bad Request: MEDIA_CAPTION_TOO_LONG'):
            parse_mode = params.get('parse_mode')
            limit, key = (4096, 'text') if 'text' in params else (1024, 'caption')
            text = params[key]
            # todo: text division
        if res['ok'] is True:
            return res['result']
        else:
            raise Exception(Logger().log(res))

    def sendMessage(self, text: str, **params) -> dict:
        return self.method('sendMessage', text=text, **params)

    def sendPhoto(self, file_path: Optional[str] = None, **params) -> dict:
        return self.method('sendPhoto', file_path=file_path, file_type='photo', **params)

    def sendDocument(self, file_path: Optional[str] = None, **params) -> dict:
        return self.method('sendDocument', file_path=file_path, file_type='document', **params)

    def sendMessageSilently(self, text: str, filler: str = '...', delay: Union[int, float] = 0.25, **params) -> dict:
        message_id = self.sendMessage(filler, **params)['message_id']
        sleep(delay)
        return self.method('editMessageText', text=text, message_id=message_id,
                           **dict((key, params[key]) for key in params if key in
                                  ('chat_id', 'inline_message_id', 'parse_mode',
                                   'disable_web_page_preview', 'reply_markup')))

    def answerCallbackQuery(self, callback_query_id: int, **params) -> dict:  # todo check return type
        return self.method('answerCallbackQuery', callback_query_id=callback_query_id, **params)

    def cache_user(self, user_or_user_containing_object: dict) -> None:
        if self.user_cache is not None:
            Thread(target=self.user_cache.add, args=(user_or_user_containing_object,)).start()

    def cache_chat(self, chat_or_chat_containing_object: dict) -> None:
        if self.chat_cache is not None:
            Thread(target=self.chat_cache.add, args=(chat_or_chat_containing_object,)).start()

    @safeguard(5)
    def get_updates(self, offset: int = 0) -> list:
        res = get(self.api_link + 'getUpdates', params={'offset': offset}, timeout=5).json()
        if res['ok']:
            res = res['result']
            for u in res:
                self.cache_user(u)
                self.cache_chat(u)
            return res
        else:
            raise Exception(res['result'])

    @safeguard(1, True)
    def get_and_process_updates(self, offset: int = 0, queue: Optional[Queue] = None, logger: Optional[Logger] = None,
                                chats_not_to_log_to_telegram: Optional[Container[int]] = None) -> RetriesLog:
        if logger is None:
            logger = Logger()
        updates = self.get_updates(offset)
        logger.log(f'Updates for {self.username} received', sep=' ', send=False)
        for upd in updates:
            offset = max(offset, upd['update_id'] + 1)
            if queue is not None:
                queue.put(upd)
            chat_id = get_chat_id(upd)
            logger.log(upd, file_name=str(chat_id),
                       send=(chat_id not in chats_not_to_log_to_telegram) if chats_not_to_log_to_telegram is not None
                       else (self.chat_cache is None or
                             self.chat_cache.get_number_of_messages(chat_id) < self.mnomtacnwltt))
        return offset, updates

    def download_file(self, file_id: str, file_name: Optional[str] = None,
                      file_name_salt: Optional[str] = None) -> str:
        if file_name is None:
            from time import time
            file_name = time()
        if file_name_salt is None:
            from random import randint
            file_name_salt = randint(0, 239)
        file_path = self.method('getFile', file_id=file_id)['file_path']
        file_name = f'{file_name}_{file_name_salt}.{file_path.split(".")[-1]}'
        with open(file_name, 'wb') as o:
            o.write(get(f'https://api.telegram.org/file/bot{self.token}/{file_path}').content)
        return file_name

    def extract_and_download_voice(self, message: dict, file_name: Optional[str] = None,
                                   file_name_salt: Optional[str] = None) -> Optional[str]:
        return None if (voice := extract_media(message, 'voice')) is None \
            else self.download_file(voice['id'], file_name=file_name, file_name_salt=file_name_salt)

    def download_photo(self, file_info: dict, file_name: Optional[str] = None, file_name_salt: Optional[str] = None,
                       resolution_picker=lambda x: max(x, key=lambda r: r['width'] * r['height'])) -> str:
        return self.download_file(file_id=resolution_picker(file_info)['file_id'], file_name=file_name,
                                  file_name_salt=file_name_salt)

    def extract_and_download_photo(self, message: dict, file_name: Optional[str] = None,
                                   file_name_salt: Optional[str] = None,
                                   resolution_picker=lambda x: max(x, key=lambda r: r['width'] * r['height']),
                                   max_doc_size: int = 0) -> Union[str, bool, None]:
        if (photo := extract_media(message, 'photo')) is not None:
            return self.download_photo(photo, file_name, file_name_salt, resolution_picker)
        if max_doc_size > 0:
            for m in (message, message.get('reply_to_message')):
                if m is not None and (d := m.get('document')) is not None and d['mime_type'].startswith('image'):
                    if d['file_size'] <= max_doc_size:
                        return self.download_file(d['file_id'], file_name, file_name_salt)
                    else:
                        return False

    def get_command(self, message_text: str) -> str:
        if not message_text or message_text[0] != '/':
            return ''
        message_text = message_text.split()[0].split('@')
        if len(message_text) > 1 and message_text[-1].lower() != self.username.lower():
            return ''
        return message_text[0][1:].lower()

    def set_window_name(self) -> None:
        if os_name == 'nt':
            system(f'Title {self.username}')

    def is_user_allowed_to_use_admin_only_features(self, message: dict) -> bool:
        return message['from']['id'] in (administrator['user']['id'] for administrator in
                                         self.method('getChatAdministrators', chat_id=message['chat']['id'])) \
            if message['chat']['type'] == 'supergroup' else True

    # todo: status sender
