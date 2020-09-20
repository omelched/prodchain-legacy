import os
import logging
import sys

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")


def _get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        logger.handlers = []
    logger.addHandler(_get_console_handler())
    logger.propagate = False
    return logger


class LoggedBaseException(BaseException):
    logger = get_logger('ErrorLogger')

    def __init__(self, message: str = None):
        super().__init__(message)

        self.logger.error(str(self))

    def __str__(self):
        return str(self.__class__).split('\'')[1]


class InitializationException(LoggedBaseException):
    pass


class ApplicationInitializationException(InitializationException):
    pass


class Config:
    if 'HEROKU' in list(os.environ.keys()):
        ON_HEROKU = os.environ['HEROKU']
    else:
        ON_HEROKU = False

    if 'UNSTABLE' in list(os.environ.keys()):
        SUFFIX = '-unstable'
    else:
        SUFFIX = ''
