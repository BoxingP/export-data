import inspect
import json
import logging
import logging.config
import os
import time
from functools import wraps

from utils.config import config


class Logger(object):
    def __init__(self, name=None, default_path=os.path.join(os.path.dirname(__file__), 'logging_config.json'),
                 default_level=logging.DEBUG):
        self.path = default_path
        self.level = default_level
        self.caller_name = name
        if self.caller_name is None:
            self.detect_caller_info()
        with open(self.path, 'r', encoding='UTF-8') as file:
            logging_config = json.load(file)
        logging_config["handlers"]["info_file"]["filename"] = str(config.LOG_FILE_PATH)
        self.logger = self.get_logger(f'{self.caller_name}', logging_config)
        return

    def get_logger(self, name, logging_config):
        logging.config.dictConfig(logging_config)
        logging.Formatter.converter = time.localtime
        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        return logger

    def detect_caller_info(self):
        stack = inspect.stack()
        try:
            caller_frame = stack[2]
            if 'self' in caller_frame.frame.f_locals:
                caller_class = caller_frame.frame.f_locals['self'].__class__.__name__
                caller_method = caller_frame.frame.f_code.co_name
                self.caller_name = f'{caller_class}.{caller_method}'
            else:
                self.caller_name = caller_frame.frame.f_globals.get('__name__', None)
        except (AttributeError, IndexError):
            self.caller_name = None

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
