import datetime
import inspect
import os
from pathlib import Path

import allure
from allure_commons.types import AttachmentType

from utils.config import config


def detect_caller_info():
    stack = inspect.stack()
    try:
        caller_frame = stack[2]
        caller_class = caller_frame.frame.f_locals['self'].__class__.__name__
        caller_method = caller_frame.frame.f_code.co_name
        caller_name = f'{caller_class}_{caller_method}'
        return caller_name.lower()
    except (AttributeError, IndexError):
        caller_name = 'screenshot'
        return caller_name


class Screenshot(object):

    @staticmethod
    def take_screenshot(driver, message, test=''):
        if test == '':
            pytest_current_test = os.environ.get('PYTEST_CURRENT_TEST')
            if pytest_current_test is not None:
                test = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0].lower()
            else:
                test = detect_caller_info()
        current = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        img_name = f'{test}_{current}.png'
        img_path = Path(config.SCREENSHOTS_DIR_PATH, img_name)
        img = driver.get_screenshot_as_file(img_path)
        if not img:
            img = driver.get_screenshot_as_file(img_path)
        with open(img_path, mode='rb') as image:
            allure.attach(image.read(), name=message, attachment_type=AttachmentType.PNG)
