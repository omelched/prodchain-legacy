import os
import time
import sys
import errno
import logging
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")

LOG_FILE = "logs/prodchain.log"


def _get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def _get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        try:
            os.makedirs(os.path.dirname(LOG_FILE))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    if logger.handlers:
        logger.handlers = []
    logger.addHandler(_get_file_handler())
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


class InvalidTXDataException(LoggedBaseException):
    pass


class Config:
    if 'HEROKU' in list(os.environ.keys()):
        ON_HEROKU = bool(os.environ['HEROKU'])
    else:
        ON_HEROKU = False

    if 'UNSTABLE' in list(os.environ.keys()):
        UNSTABLE = bool(os.environ['UNSTABLE'])
    else:
        UNSTABLE = False

    if 'TESTING' in list(os.environ.keys()):
        TESTING = bool(os.environ['TESTING'])
    else:
        TESTING = False


def get_nonzero_symbol_index(string: str = None):
    if string is None or type(string) != str:  # TODO: exception if bad type
        return 0
    return [i for i in range(len(string)) if string[i] != '0'][0]