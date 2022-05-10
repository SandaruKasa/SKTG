import requests
import datetime

import telegram

from sktg.utils import Blueprint

inspirobot = Blueprint("inspirobot")


@inspirobot.command("inspire", "inspirobot", description="AI-generated inspirational quote")
def inspire(message: telegram.Message):
    message.chat.send_chat_action(telegram.ChatAction.UPLOAD_PHOTO)

    today = datetime.date.today()
    if today.month == 12 and today.day >= 20 or today.month == 1 and today.day <= 14:
        site = "xmascardbot.com"
    else:
        site = "inspirobot.me"

    picture_url = requests.get(
        f"https://{site}/api",
        params={"generate": "true"},
    ).text

    return message.reply_photo(
        photo=picture_url,
        caption=f"https://{site}/share?iuid={picture_url.split(site)[-1].strip('/')}",
        quote=True,
    )
