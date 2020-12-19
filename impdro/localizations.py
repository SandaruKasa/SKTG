from typing import Optional, Union

from SKTools.links import github_repository_link
from SKTools.tokens import impdro_database_link, bucket
from SKTools.vk import method as vk_method

vk_link = r'https://vk.com/' + vk_method('groups.getById', group_id=abs(bucket))[0]['screen_name']


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

<b>/random</b> - скину случайный пост <a href="{vk_link}">из ВК</a>.

<b>/vk</b> или <b>/bucket</b> - скину следующий по хронологическому порядку пост <a href="{vk_link}">из ВК</a>, \
если чат подписан на регулярный постинг. Если чат не подписан, скину случайный пост.

<b>/subscribe</b> и <b>/unsubscribe</b> позволяют подписаться на регулярный постинг и отписаться от него \
соответственно. Если чат подписан на регулярный постинг, то каждые два часа бот будет автоматически запускать команду \
<b>/send</b> (без тэгов). "Каждые два часа" значит каждый нечётный час по Москве. (Только по ночам бот пока не \
работает, потому что хостится у меня на ноуте. Я, в принципе, уже почти готов сервак для работы 24/7 поднять, но мне \
чё-то всё было недосуг перекинуть на него файлы. {self.shrug()} )

<b>/db</b> или <b>/database</b> - скину картинку из <a href="{impdro_database_link}">большой базы данных</a>. Также \
могу скинуть всю базу тремя большими архивами по команде <b>/send_database</b>.

<b>/tag</b> или <b>/search</b> или <b>/find</b> - скину пост из ВК по тэгам. На вход принимются команды в духе:
    <code>/tag mituna</code>
или
    <code>/find dave_strider</code>
или
    <code>/search nepeta_leijon karkat</code>

<b>/send</b> + тэги — то же, что и <b>/tag</b> + тэги

<b>/send</b> без тэгов — запустит либо постинг из базы данных (<b>/db</b>), либо постинг из ВК (<b>/vk</b> для \
подписанных на рассылку чатов и <b>/random</b> для остальных); выбор случаен.

<b>/top</b> — выведет список самых активно использующих команды пользователей из данного чата. Учитываются только \
команды на подобие /send, /random, /vk, /db и /tag. 

Код бота <a href="{github_repository_link}">есть на ГитХабе</a>.\
'''

    @staticmethod
    def empty_query() -> str:
        return 'Пожалуйста, введите поисковый запрос. Если Вы не знаете, как это делается, обратитесь к <b>/help</b>'

    def nothing_found(self) -> str:
        return f'По Вашему запросу ничего не найдено\n{self.shrug()}'

    @staticmethod
    def vk_blacklist() -> str:
        return 'Этот чат занесён в чёрный список админом группы в ВК. Мне жаль.'

    @staticmethod
    def admins_only() -> str:
        return 'Только администраторы чата могут использовать эту команду.'

    @staticmethod
    def subscribed() -> str:
        return 'Готово! Теперь этот чат подписан на рассылку!'

    @staticmethod
    def unsubscribed() -> str:
        return 'Готово! Теперь этот чат отписан от рассылки!'

    @staticmethod
    def already_subscribed() -> str:
        return 'Этот чат и так уже подписан на рассылку.'

    @staticmethod
    def already_unsubscribed() -> str:
        return 'Этот чат и так уже отписан от расслыки.'

    @staticmethod
    def loading() -> str:
        return 'Секунду...'

    @staticmethod
    def chat_top_header(chat_name: str) -> str:
        return f'Самые активные пользователи чата <i>{chat_name}</i>:\n\n'

    @staticmethod
    def user_top_header() -> str:
        return '''\
Вообще я рассчитывал, что эту команду будут использовать в групповых чатах, а не в личке с ботом, но раз так, то вот \
тебе список чатов, где ты использовал команды наибольшее число раз:

'''

    @staticmethod
    def no_data_yet() -> str:
        return 'Данных пока нет'


class English(Language):
    def greeting(self) -> str:
        return 'Hey!'

    def help(self) -> str:
        return f'''\
{self.greeting()} My name is Imperial Drone. I'm a bot created by {self.creator}. And here's what I can do:

<b>/start</b> or <b>/help</b> — will display this message

<b>/random</b> - will send a random post <a href="{vk_link}">from VK</a>

<b>/vk</b> or <b>/bucket</b> - will send the chronologically next post <a href="{vk_link}">from VK</a> if the chat is \
subscribed to regular posting. If chat is not subscribed, this will work as <b>/random</b>.

<b>/subscribe</b> & <b>/unsubscribe</b> - will subscribe the chat to and unsubscribe it from the regular posting. \
What is the regular posting? If the chat is subscribed to it, the bot will automatically execute <b>/send</b> command \
(without any tags) every two hours. (Except during European nighttime, because the bot is hosted on my PC so far.) \
"Every two hours" basically means at every ??:00 UTC where ?? is even.  

<b>/db</b> or <b>/database</b> - will send a picture from <a href="{impdro_database_link}">a big database</a>. To get \
the entire database as archives uploaded to Telegram, use <b>/get_database</b>.

<b>/tag</b> or <b>/search</b> or <b>/find</b> - this command + a tag will make the bot find a VK post with the \
corresponding character(s); stuff like
    <code>/tag mituna</code>
or
    <code>/find dave_strider</code>
or
    <code>/search nepeta_leijon karkat</code>
is expected.

<b>/send</b> with tags will work like <b>/tag</b>

<b>/send</b> without tags will work like either <b>/db</b> or <b>/vk</b>, chosen randomly. In case chat is not \
subscribed to regular posting, <b>/random</b> will be used instead of <b>/vk</b>.

<b>/top</b> — will show a top of the users in this chat who use commands most actively. Only commands like /send, \
/random, /vk, /db, and /tag are counted.

My source code is <a href="{github_repository_link}">available on github</a>.\
'''

    @staticmethod
    def empty_query() -> str:
        return 'Please enter a search query. If you don\'t know how to do it, refer to <b>/help</b>'

    def nothing_found(self) -> str:
        return f'Nothing found\n{self.shrug()}'

    @staticmethod
    def vk_blacklist() -> str:
        return 'This chat had been blacklisted from using the VK group. Sorry.'

    @staticmethod
    def admins_only() -> str:
        return 'Only chat administrators can use this command.'

    @staticmethod
    def subscribed() -> str:
        return 'Done! The chat is now subscribed to regular posting.'

    @staticmethod
    def unsubscribed() -> str:
        return 'Done! The chat is now unsubscribed from regular posting.'

    @staticmethod
    def already_subscribed() -> str:
        return 'The chat had already been subscribed to regular posting.'

    @staticmethod
    def already_unsubscribed() -> str:
        return 'The chat had already been unsubscribed from regular posting.'

    @staticmethod
    def loading() -> str:
        return 'Loading...'

    @staticmethod
    def chat_top_header(chat_name: str) -> str:
        return f'Top active members of <i>{chat_name}</i>:\n\n'

    @staticmethod
    def user_top_header() -> str:
        return '''\
This command isn't supposed to be used outside of group chats, but since you've used it in private messages with the \
bot, here's the list of chats you have been most active in:

'''

    @staticmethod
    def no_data_yet() -> str:
        return 'No data yet'


class Italian(English):
    def greeting(self) -> str:
        return 'Ciao!'

    def help(self) -> str:
        return f'''\
{self.greeting()} Il mio nome è imperial Drone. Sono un bot sviluppato da {self.creator}, \
ecco una lista di cose che posso fare:

<b>/start</b> o <b>/help</b> - ti invierà questo messaggio con i comandi

<b>/random</b> - ti invierà un'immagine casuale <a href="{vk_link}">da VK</a>

<b>/vk</b> o <b>/bucket</b> - ti invierà il post successivo nella lista <a href="{vk_link}">di VK</a>, se la chat è \
iscritta a invii regolari, altrimenti manderà un'immagine casuale.

<b>/subscribe</b> & <b>/unsubscribe</b> - iscriverà la chat e cancellerà l'iscrizione all'invio regolare di contenuti. \
Cosa è l'invio regolare? Se la chat ne è iscritta il bot invierà automaticamente il comando <b>/send</b> ogni due ore. \
(Escludendo il fusoriario notturno europeo perche il bot è hostato sul mio pc per ora) 

<b>/db</b> o <b>/database</b> ti invierà un'immagine da un <a href="{impdro_database_link}">database</a>. Per accedere \
all'intero database usa <b>/get_database</b> 

<b>/tag</b> o <b>/search</b> o <b>/find</b> - questi comando seguito da un tag dirà al bot di cercare un'immagine su \
VK correlata al tag inserito, ad esempio
    <code>/tag mituna</code>
    <code>/find dave_strider</code>
    <code>/search nepeta_leijon karkat</code>

Se utilizzi il comando <b>/send</b> con un tag funzionerà come il comando <b>/tag</b>

Il comando <b>/send</b> senza alcun tag funzionerà o come <b>/db</b> o <b>/vk</b>, scelto casualmente.

<b>/top</b> — ti manderà una lista degli utenti che più usano i comandi: /send, /random, /vk, /db, e /tag.

Il mio codice sorgente è <a href="{github_repository_link}">disponibile su github</a>. \
Traduzione in italiano di @Bluehoundclaws.\
'''

    def nothing_found(self) -> str:
        return f'Il bot non trova proprio nulla.\n{self.shrug()}'

    @staticmethod
    def empty_query() -> str:
        return 'Per favore inserisci una domanda di ricerca, se non sai come fare utilizza il comando <b>/help</b>'

    @staticmethod
    def vk_blacklist() -> str:
        return 'Questa chat è stata bannata dalla lista di chat a cui è possibile accedere al database VK, mi dispiace.'

    @staticmethod
    def admins_only() -> str:
        return 'Questo comando è riservato agli amministratori.'

    @staticmethod
    def subscribed() -> str:
        return 'Fatto! Ora la chat è iscritta agli invii regolari!'

    @staticmethod
    def unsubscribed() -> str:
        return 'Fatto! Ora la chat non è più iscritta agli invii regolari!'

    @staticmethod
    def already_subscribed() -> str:
        return 'La chat già è iscritta agli invii regolari.'

    @staticmethod
    def already_unsubscribed() -> str:
        return 'La chat è già stata eliminata dalla lista degli invii regolari.'

    @staticmethod
    def loading() -> str:
        return 'Caricamento...'

    @staticmethod
    def chat_top_header(chat_name: str) -> str:
        return f'Utenti più attivi di <i>{chat_name}</i>:\n\n'

    @staticmethod
    def user_top_header() -> str:
        return '''\
Questo comando non funziona al di fuori delle chat di gruppo, ma dal momento che lo stai usando nella chat privata del \
bot, ecco a te la lista delle chat dove sei stato più attivi:

'''

    @staticmethod
    def no_data_yet() -> str:
        return 'Ancora nessun dato'


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
