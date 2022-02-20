import telegram.ext

from sktg.utils import Blueprint
from .logger import format_update

debugger = Blueprint("debugger")


def print_update(update: telegram.Update | str, context: telegram.ext.CallbackContext):
    print(format_update(update))


# subscribe to EVERY update
class UniversalHandler(telegram.ext.Handler):
    def check_update(self, update) -> bool:
        return True


debugger.add_handler(UniversalHandler(callback=print_update))
