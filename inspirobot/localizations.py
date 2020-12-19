from typing import Optional, Union

from SKTools.links import github_repository_link
from SKTools.tokens import impdro_database_link, bucket
from SKTools.vk import method as vk_method


class Language:
    creator = '@SandaruKasa'

    @staticmethod
    def shrug() -> str:
        return r'¯\_(ツ)_/¯'


class Russian(Language):
    def greeting(self) -> str:
        return 'Привет!'

    def help(self) -> str:
        return f'''\
{self.greeting()} Я — Имперский Дрон (бот, сделанный {self.creator}) и вот что я умею:

<b>/start</b> или <b>/help</b> — выведу это сообщение


Код бота <a href="{github_repository_link}">есть на ГитХабе</a>.\
'''


class English(Language):
    def greeting(self) -> str:
        return 'Hey!'

    def help(self) -> str:
        return f'''\
{self.greeting()} My name is Imperial Drone. I'm a bot created by {self.creator}. And here's what I can do:

<b>/start</b> or <b>/help</b> — will display this message


My source code is <a href="{github_repository_link}">available on github</a>.\
'''


class Italian(English):
    def greeting(self) -> str:
        return 'Ciao!'

    def help(self) -> str:
        return f'''\
{self.greeting()} Il mio nome è imperial Drone. Sono un bot sviluppato da {self.creator}, \
ecco una lista di cose che posso fare:

<b>/start</b> o <b>/help</b> - ti invierà questo messaggio con i comandi


Il mio codice sorgente è <a href="{github_repository_link}">disponibile su github</a>. \
Traduzione in italiano di @Bluehoundclaws.\
'''


class Ukrainian(Russian):
    def greeting(self) -> str:
        return f'Слава Україні! Создатель бота, к сожалению, не розмовляє українською, так что усё будет на русском,\
извиняйте {self.shrug()} <i>*А дальше текст, который я написал для русской локализации…*</i>\n\nПривет!'


languages = {
    'en': English(),
    'ru': Russian(),
    'it': Italian(),
    'uk': Ukrainian()
}


def strings(lang_code: Optional[str] = (default := 'en')) -> Union[English, Russian, Italian, Ukrainian]:
    return lang_code and languages.get(lang_code.lower(), None) or languages[default]
