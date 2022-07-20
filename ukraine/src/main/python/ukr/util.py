import logging
from logging import Formatter


def i_am_on_server():
    import os
    return os.name == 'posix'


def default_root():
    return '.' if i_am_on_server() else 'c:/data/ukr'


class MyFormatter(Formatter):
    default_msec_format = '%s.%03d'

    def __init__(self, fmt=None, datefmt=None, timefmt=None):
        super().__init__(fmt, datefmt)
        self.timefmt = timefmt

    def formatTime(self, record, datefmt=None):
        import time

        ct = self.converter(record.created)

        timefmt = self.timefmt if self.timefmt is not None else '%H:%M:%S'
        stime = time.strftime(timefmt, ct)
        if self.default_msec_format:
            stime = self.default_msec_format % (stime, record.msecs)

        datefmt = datefmt if datefmt is not None else '%Y-%m-%d'
        sdate = time.strftime(datefmt, ct)

        return f'{stime} @ {sdate}'


def init_logging(level=logging.INFO,
                 fmt='[%(levelname)4s] %(asctime)s {%(module)s.%(funcName)s}: %(message)s'):
    import logging
    sh = logging.StreamHandler()
    sh.setFormatter(MyFormatter(fmt=fmt))
    logging.basicConfig(level=level, handlers=[sh])
