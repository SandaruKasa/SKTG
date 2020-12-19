from typing import Optional, Union, Final

from SKTools.links import github_repository_link
from SKTools.tokens import me

interpolation_methods: Final = ('NEAREST', 'BOX', 'BILINEAR', 'HAMMING', 'BICUBIC', 'LANCZOS')
max_image_size: Final = 10_000_000


class Language:
    @staticmethod
    def shrug() -> str:
        return r'¯\_(ツ)_/¯'

    creator = '@SandaruKasa'


class Russian(Language):
    @staticmethod
    def greeting() -> str:
        return 'Привет!'

    def help(self) -> str:
        return f'''\
{self.greeting()} Я бот по имени β Lupi (AKA @Kekouan_bot). Мой создатель — {self.creator}. А вот, что я умею:

<b>/start</b> или <b>/help</b> — выведу это сообщение

<b>/shrug</b> — пришлю {self.shrug()} в ответ

<b>/jpeg [уровень сжатия]</b> — зашакалю фото, которое подписали или на которое ответили этой командой. Уровень сжатия \
— целое число от 1 до 10. Можно не указывать. По умолчанию 5.

<b>/quote</b> — сделаю цитату из сообщения, на которое ответили командой. (бета)

<b>/demotivator</b> — сделаю демотивтаор. (бета) Подробнее: /help_demotivator

<b>/sticker</b> — подгоню размер изображения под стикер. Подробнее: /help_sticker

<b>/coordinates</b> — наложу на картинку <a href="https://i.kym-cdn.com/photos/images/facebook/001/225/876/fb8.jpg">\
политические координаты</a> (пока что не работает).

<b>/mspabooru [тэги]</b> — скину рандомный артик с mspabooru.com по данным тэгам. Подробнее: /help_tags

<b>/safebooru [тэги]</b> — то же, но с safebooru.org (работает медленно, спасибо Роскомнадзору)

<b>/olive</b> — скину артик из <a href="https://vk.com/nepetafans">одной группы в ВК</a>.

<b>/mp3</b> — сконвертирую голосовое в .mp3 файл

По команде /help_extended расскажу про альтернативные названия команд и принудительную отправку картинок документами.

Мой код <a href="{github_repository_link}">есть на ГитХабе</a>.\
'''

    @staticmethod
    def help_extended() -> str:
        return f'''\
Во-первых, у некоторых команд есть альтернативные варианты. Например, вместо /demotivator можно писать /dem и работать \
всё будет точно так же. Список альтернативных вариантов:

/jpeg: /jpg, /compress, /compression
/demotivator: /dem, /d
/quote: /qt, /q
/sticker: /resize
/coordinates: /political_coordinates, /pc, /pol, /coord

Во-вторых, к командам для цитат, демотиваторов и политических координат можно добавлять <i>doc</i> (например, /demdoc,\
 /quotedoc, /poldoc и т.д.), чтобы бот отправил результат как документ. Если этого не делать, то бот будет отправлять \
документом, только если одна из сторон итогового изображения больше другой минимум в три раза. Команды для стикеров \
добавления <i>doc</i> не поддерживают, потому что и так кидают результат документом. Ещё это не поддерживают команды \
для зашакаливания фоток, а то уж слишком абсурдно.

В-третьих, похожая возможность есть для команд /mspabooru и /safebooru, только меняются они на /mspadoc и /safedoc,
а без этого отправять картинки документами будут, если хотя бы одна из сторон не меньше 1920 пикселей.

В-четвёртых, если входное изображение скинуто документом, то его размер не должен превышать \
{max_image_size // 1_000_000} МБ.\
'''

    @staticmethod
    def help_tags() -> str:  # todo
        return f'''\
Извиняюсь, этот раздел я ещё не написал, потому что пилю локализации и новые справки в час ночи.\
'''

    @staticmethod
    def help_demotivator() -> str:
        return f'''\
Так, о демотиваторах.

Во-первых, <b>откуда же берётся текст для демотиватора</b>? А присылаете его Вы. Крупным текстом в верхней части \
подписи становится вся первая строка сообщения, за вычетом команды и идущего за ней пробела. Все остальные строки \
становятся текстом меньшего размера и внизу. По желанию, можно пропустить большой текст, отступив на новую строку \
сразу после команды, или пропустить весь маленький текст, просто не переходя но новую строчку в сообщении.

Т.е. в демотиваторе, созданном по команде<code>
    /demotivator LMAO
    bottom
    text</code>
<i>LMAO</i> будет крупным, а <i>bottom</i> и <i>text</i> — мелкими (сама же команда /demotivator и пробел между ней \
и <i>LMAO</i> в демотиватор не войдут); в демотиваторе, по команде<code>
    /demotivator
    LMAO
    bottom
    text</code>
мелкими будут все строки, а по команде<code>
    /demotivator LMAO bottom text</code>
все будут крупными.

Во-вторых, <b>Откуда же берётся изображение для демотиватора</b>? Сначала бот ищет изображение в сообщении, \
в котором была команда. Т.е. если вы отправите изображение, а подписью к нему будет команда, то демотиватор будет \
сделан из этого изображения. Если в сообщении с коммандой изображений не было, бот проверит, ответили ли Вы командой \
на какое-то сообщение. Если нет, то демотиватора Вам не видать, сожалею. Если всё-таки ответили, бот проверит, есть ли \
изображение в сообщении, на которое ответили. Если есть, то демотиватор будет сделан из него. Если нет, то бот \
попытается сделать цитату из этого сообщения (как по команде /quote), а затем воспользоваться цитатой как картинкой \
для демотиватора. Это ему удасться, только если в том сообщении был текст. Т.е. при ответе на голосовое или на стикер \
(текста там нет) цитату сделать у бота не выйдет. Тогда он совершит последнюю отчаянную попытку и запилит демотиватор \
с аватаркой того, на чьё сообщение Вы ответили. (Если же аватарки нет или она скрыта, то бот по-быстрому склепает \
картинку с инициалами и воспользуется ею).

Кстати, посоветуйте, пожалуйста, шрифт с поддержкой всякой японокитайщины и прочего. \
А то у меня даже мой ник на цитатах нормально не отображается. (Советовать <a href="tg://user?id={me}">сюда</a>.)\
'''

    @staticmethod
    def help_sticker() -> str:
        return f'''\
Если Вам когда-нибудь доводилось делать стикеры для телеги, то Вы наверное знаете, что она требует, чтобы одна из \
сторон изображения была 512 пикселей, а другая — ≤512. Команда /sticker у этого бота как раз таки и уменьшает/\
увеличивает избражения до нужного размера. Дополнительно, кстати, можно указать метод интерполяции. Например,<code>
    /sticker BICUBIC</code>
или<code>
    /sticker nearest</code>
Заглавные/строчные роли не играют, по умолчанию стоит BICUBIC, все доступные методы:
{', '.join(f'<code>{i}</code>' for i in interpolation_methods)}

Если Вы не знаете, что это всё значит, то не обращайте внимания и просто используйте команду без всяких дополнительных \
параметров. Правда, если вдруг у какой-то картинки острые углы или резкие преходы окажутся замыленными после обработки,\
 попробуйте <code>/sticker nearest</code>.\
'''

    def ttl_error_message(self) -> str:
        return f'''\
У меня не получилось сделать то, что Вы попросили, даже после нескольких попыток. 3:
Пожалуйста, сообщите {self.creator} о том, что сейчас произошло.\
'''


class English(Language):
    @staticmethod
    def greeting() -> str:
        return 'Hey!'

    def help(self) -> str:
        return f'''\
{self.greeting()} My name is β Lupi (AKA @Kekouan_bot). I'm a bot created by {self.creator}, and here's what I can do:

<b>/start</b> or <b>/help</b> — will display this message

<b>/shrug</b> — will send a {self.shrug()} in response

<b>/jpeg [compression lvl]</b> — will cover a photo with jpeg artifacts. You should reply with this command to a photo \
or put it as a caption. Compression level is an optional integer, 1 to 10. Default is 5. The higher the level, \
the more artefacts.

<b>/quote</b> — will turn a message you've replied with this command to into a quote (beta)

<b>/demotivator</b> — will create a demotivator. (beta) More info: /help_demotivator

<b>/sticker</b> — will make an image fit for a sticker. More info: /help_sticker

<b>/coordinates</b> — will overlay <a href="https://i.kym-cdn.com/photos/images/facebook/001/225/876/fb8.jpg">\
political coordinates</a> over a picture (doesn't work yet, sorry).

<b>/mspabooru [tags]</b> — will send a random artwork with this tags from mspabooru.com, more info: /help_tags

<b>/safebooru [tags]</b> — same as above, but safebooru.org (works slowly because the site is blocked in Russia \
for no good reason)

<b>/olive</b> — will send an artwork from <a href="https://vk.com/nepetafans">a VK group</a>.

<b>/mp3</b> — will convert a voice message into a .mp3 file 

Use /help_extended to learn about alternative names of the commands and how to make the bot send pictures via documents.

Bot's source code <a href="{github_repository_link}">is available on GitHub</a>.\
'''

    @staticmethod
    def help_extended() -> str:
        return f'''\
First of all, some commands have alternative names (aliases). For example, you can type /dem instead of /demotivator \
and it'll work just fine. The complete list of aliases:

/jpeg: /jpg, /compress, /compression
/demotivator: /dem, /d
/quote: /qt, /q
/sticker: /resize
/coordinates: /political_coordinates, /pc, /pol, /coord

Secondly, you can add <i>doc</i> to commands for quotes, demotivator, and political coordinates (for example, /demdoc, \
/quotedoc, /poldoc, etc.). This will make the bot send the result via a document (without compression). Otherwise \
pictures will be sent in the regular Telegram's way for uploading photos, unless a picture has a side ratio of 1:3 \
(3:1) or worse. /sticker commands do not have this feature because they always send the result via a document. /jpeg \
commands do not have it either because it would be absurd if they did.  

Thirdly, a similar feature exists for /mspabooru & /safebooru, though their "compression-free" versions are /mspadoc & \
/safedoc. And the reason for /mspabooru & /safebooru to send the result without compression is not the side ratio but \
at least one side being 1920 pixels or longer.

Lastly, input images for /jpeg, /demotivator, etc. shouldn't be larger than {max_image_size // 1_000_000} MB is they \
are sent via a document.\
'''

    @staticmethod
    def help_tags() -> str:  # todo
        return f'''\
I haven't written this section yet, sorry.\
'''

    @staticmethod
    def help_demotivator() -> str:
        return f'''\
Well, what is a demotivator? It's a picture like <a href="https://pbs.twimg.com/media/DsSy7z1WsAAdtKL.jpg">this one\
</a>. Basically you take an image, give it a black frame and some white caption below. It was a popular thing in \
Russia ten years ago and nowadays it is popular again. So, the bot can create demotivators for you.  

But how does it choose a caption? It's simple, <i>you</i> send it. The caption is usually divided into two parts, big \
upper text and smaller bottom text. For the big upper text the bot will take the first line of your message excluding \
the command itself. Everything else becomes the smaller bottom text. If you wish, you can skip the upper text by not \
writing anything on the same line with the command, or you can skip the bottom text by having only one line in your \
message.

Thus, using<code>
    /demotivator LMAO
    bottom
    text</code>
will result into <i>LMAO</i> being the big upper text, and <i>bottom</i> & <i>text</i> being the smaller bottom text. \
Using<code>
    /demotivator
    LMAO
    bottom
    text</code>
will result into everything being the smaller bottom text, and using<code>
    /demotivator LMAO bottom text</code>
will make everything the big upper text.

There is also an algorithm to how the bot chooses what image to make a demotivator with. When you send an image and \
its caption is the command, the bot will use this image. If the message with the command doesn't have an image in it, \
the bot will check whether this message is a reply to another message. If it is not, then no demotivator for you, pal. \
If it is, the bot will check whether there is an image in that message. If there is, it will be used for the \ 
demotivator. If there is not, the bot will try to turn that message into a quote (just like with the /quote command). \
This will work only if that message has some text in it. So if that message is a sticker or a voice message, the quote \
won't be generated and the bot won't be able to use it for the demotivator. In this case, the bot will use the profile \
picture of the user whose message you've replied to. (If they have no profile picture or their profile picture is \
hidden, the bot will generate a picture with users' initials to use instead of the missing profile picture.)

P.S. I would really appreciate it if you could recommend <a href="tg://user?id={me}">me</a> a typefont that supports \
Japanese, Chinese, Korean characters, emoji and stuff.\
'''

    @staticmethod
    def help_sticker() -> str:
        return f'''\
If you've ever tried making Telegram stickers, you probably know that it asks you to provide a .png image with one of \
the sides being 512 pixels long, and the other — ≤512. The /sticker command of this bot does exactly this. It makes an \
image fit the size of a sticker. Additionally, you can choose an interpolation filter. For example,
<code>    /sticker BICUBIC</code>
or
<code>    /sticker nearest</code>
Not case-sensitive, defaults to BICUBIC. List of available methods:
{', '.join(f'<code>{i}</code>' for i in interpolation_methods)}

If you don't know what all this means, then simply use
<code>    /sticker</code>
without caring about any interpolation methods at all. Though if a result image happens to be too blurry, try using
<code>    /sticker nearest</code>
instead.\
'''

    def ttl_error_message(self) -> str:
        return f'''\
I made several attempts to do what you asked, but I couldn't... 3:
Please, tell {self.creator} about what happened.\
'''


class Italian(English):
    def greeting(self) -> str:
        return 'Purtroppo non parlo italiano, quindi… Inglese.'


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


def strings(langcode: Optional[str] = (default := 'en')) -> Union[English, Russian, Italian, Ukrainian]:
    return langcode and languages.get(langcode.lower(), None) or languages[default]


def get_help_text(command: str, langcode: str = default) -> str:
    lang = strings(langcode)
    if command == 'help_extended':
        return lang.help_extended()
    elif command == 'help_tags':
        return lang.help_tags()
    elif command == 'help_demotivator':
        return lang.help_demotivator()
    elif command == 'help_sticker':
        return lang.help_sticker()
    else:
        return lang.help()
