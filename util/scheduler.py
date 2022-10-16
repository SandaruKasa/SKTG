import datetime

import timeloop

_tl = timeloop.Timeloop()
for _handler in _tl.logger.handlers:
    _tl.logger.removeHandler(_handler)


def job(interval: datetime.timedelta):
    return _tl.job(interval)


def start():
    return _tl.start()
