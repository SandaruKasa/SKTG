from SKTools.links import telegram_bot_api
from SKTools.proxies import proxy_request


def reply_dict(message):
    return {'chat_id': message['chat']['id'], 'reply_to_message_id': message['message_id']}


def extract_media(message, media_type):
    if media_type in message:
        return message[media_type]
    elif 'reply_to_message' in message and media_type in message['reply_to_message']:
        return message['reply_to_message'][media_type]
    else:
        return None


class Bot:
    def __init__(self, token):
        self.token = token
        self.api_link = telegram_bot_api.format(self.token)
        self.me = self.method('getMe')['result']
        self.username = self.me['username']

    def method(self, method, file=None, file_type='document', **params):
        kwargs = {'params': params}
        if file:
            kwargs['files'] = {file_type: file}
        res = proxy_request(self.api_link + method, get_and_not_post=False, **kwargs).json()
        if res.get('description') == 'Bad Request: reply message not found':
            kwargs['params'].pop('reply_to_message_id', None)
            res = proxy_request(self.api_link + method, get_and_not_post=False, **kwargs).json()
        return res

    def get_updates(self, offset=0):
        return proxy_request(self.api_link + 'getUpdates', params={'offset': offset}).json()['result']

    def download_file(self, file_id, file_name=None, file_name_salt=None):
        if file_name is None:
            from time import time
            file_name = time()
        if file_name_salt is None:
            from random import randint
            file_name_salt = randint(0, 239)
        file_path = self.method('getFile', file_id=file_id)['result']['file_path']
        file_name = f'{file_name}_{file_name_salt}.{file_path.split(".")[-1]}'
        with open(file_name, 'wb') as o:
            o.write(proxy_request(f'https://api.telegram.org/file/bot{self.token}/{file_path}').content)
        return file_name

    def download_photo(self, file_info, file_name=None, file_name_salt=None,
                       resolution_picker=lambda x: max(x, key=lambda r: r['width'] * r['height'])):
        return self.download_file(file_id=resolution_picker(file_info)['file_id'], file_name=file_name,
                                  file_name_salt=file_name_salt)

    def get_command(self, message_text):  # todo: maybe use message entities instead of parsing text
        if message_text[0] != '/':
            return ''
        message_text = message_text.split()[0].split('@')
        if len(message_text) > 1 and message_text[-1].lower() != self.username.lower():
            return ''
        return message_text[0][1:].lower()

    # todo: status sender
