# -*- coding: utf-8 -*-
# @Time    : 2020-01-09
# @File    : procBootLogger
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp


from logging import getLogger, Formatter
from logging.handlers import RotatingFileHandler

"""
logging level:
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
"""


def singleton(myclass):
    """
    for singleton pattern
    :param myclass: Logger() class
    :return:
    """
    instance = {}

    def get_instance(*args, **kwargs):
        if myclass not in instance:
            instance[myclass] = myclass(*args, **kwargs)
        return instance[myclass]

    return get_instance


@singleton
class Logger(object):
    _DEFAULT_FORMAT = '%(asctime)s, %(levelname)s, %(name)s: [%(filename)s:%(funcName)s: line %(lineno)d] %(message)s'
    _DEFAULT_DATEFMT = '%Y/%m/%d %H:%M:%S'
    _DEFAULT_LEVEL = 'INFO'
    _DEFAULT_MAXBYTES = 50000000
    _DEFAULT_BACKUPCOUNT = 3

    def __init__(self, filename=None):
        formatter = Formatter(fmt=self._DEFAULT_FORMAT,
                              datefmt=self._DEFAULT_DATEFMT, )

        self.log = getLogger("procServ")
        try:
            self.handler = RotatingFileHandler(filename, mode='a', maxBytes=self._DEFAULT_MAXBYTES,
                                               backupCount=self._DEFAULT_BACKUPCOUNT)
            self.handler.formatter = formatter
            self.handler.setLevel(self._DEFAULT_LEVEL)
            self.log.setLevel(self._DEFAULT_LEVEL)
            self.log.addHandler(self.handler)
        except Exception:
            pass

    @property
    def logger(self):
        return None

    @logger.getter
    def logger(self):
        return self.log

    @property
    def level(self):
        return


if __name__ == '__main__':
    logger = Logger('test.log')
    try:
        2 / 0
    except ZeroDivisionError:
        logger.logger.error("divide 0", exc_info=True)
    logger.logger.warning("hello warning")
    print(logger)
