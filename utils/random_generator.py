import os
import random
from time import sleep

from utils.config import config


def random_browser():
    selected_browser = random.choice(config.BROWSER_LIST)
    print(f"Using {selected_browser} to do the test.")
    os.environ['BROWSER'] = selected_browser


def random_sleep():
    start = round(random.random(), 1) * 10
    stop = random.randint(*config.SLEEP_TIME_UPPER_LIMIT_RANGE)
    seconds = round(random.uniform(start, stop), 5)
    print(f"Random sleeping {seconds} seconds ...")
    sleep(seconds)
