import os
import random
from time import sleep

from utils.config import config
from utils.logger import Logger


def random_browser():
    selected_browser = random.choice(config.BROWSER_LIST)
    Logger().info(f'Using {selected_browser} to do the test.')
    os.environ['BROWSER'] = selected_browser


def random_sleep():
    start = round(random.random(), 1) * 10
    stop = random.randint(*config.SLEEP_TIME_UPPER_LIMIT_RANGE)
    seconds = round(random.uniform(start, stop), 5)
    Logger().info(f'Random sleeping {seconds} seconds ...')
    sleep(seconds)
