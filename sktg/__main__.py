"""A file that starts the bots.
Created to allow running the bots with ``python3 -m sktg``.
"""
if not __package__:  # a dirty hack to ensure this is run as a module
    import os
    import sys
    from pathlib import Path

    module_dir = Path(__file__).parent.resolve()
    module_name = module_dir.name
    expected_pwd = module_dir.parent

    os.chdir(expected_pwd)
    return_code = os.system(f"{sys.executable} -m {module_name}")
    exit(return_code)

import logging

from . import persistence, scheduler, telegram
from .features import dice, inspirobot, jpeg, misc, shorts, shrooms

logging.info("Starting...")
persistence.init()
scheduler.start()
telegram.start_polling()
