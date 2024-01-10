import inspect
import json
import logging
import logging.config
import os
import time
from functools import wraps

from utils.config import config


class Logger(object):
    def __init__(self, name, default_path=os.path.join(os.path.dirname(__file__), 'logging_config.json'),
                 default_level=logging.DEBUG):
        self.path = default_path
        self.level = default_level
        with open(self.path, 'r', encoding='UTF-8') as file:
            logging_config = json.load(file)
        logging_config["handlers"]["info_file"]["filename"] = str(config.LOG_FILE_PATH)
        self.logger = self.get_logger(name, logging_config)
        return

    def get_logger(self, name, logging_config):
        logging.config.dictConfig(logging_config)
        logging.Formatter.converter = time.gmtime
        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        return logger

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)


def _step(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        elapsed = (end - start) * 1000
        stack = inspect.stack()
        try:
            caller_class = stack[1][0].f_locals['self'].__class__.__name__
            caller_method = stack[1][0].f_code.co_name
            Logger(f'{caller_class}.{caller_method}.{func.__name__}').info(msg=f'{round(elapsed, 3)} ms')
        except KeyError:
            Logger(f'{func.__qualname__}').info(msg=f'{round(elapsed, 3)} ms')
        return result

    return wrapper
