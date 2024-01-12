import os

import pytest

from utils.config import config
from utils.driver_factory import DriverFactory
from utils.screenshot import Screenshot


@pytest.fixture(scope='class')
def setup(request):
    driver = DriverFactory.get_driver(os.environ.get('BROWSER'), config.BROWSER_HEADLESS_MODE)
    driver.implicitly_wait(0)
    request.cls.driver = driver
    yield request.cls.driver
    request.cls.driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f'rep_{rep.when}', rep)


@pytest.fixture(scope='function')
def screenshot_on_failure(request):
    yield
    if request.node.rep_setup.passed and request.node.rep_call.failed:
        current_test = request.node.name.split(':')[-1].split(' ')[0].lower()
        driver = request.cls.driver
        Screenshot.take_screenshot(driver, 'test call failed', test=current_test)


def pytest_addoption(parser):
    parser.addoption('--email-list', action='store', dest='email_list_str', default=None,
                     help='users emails list')


@pytest.fixture
def email_list_str(request):
    return request.config.option.email_list_str
