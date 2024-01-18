import os
import time
from pathlib import Path

import allure
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.locators import PageLocators
from utils.config import config
from utils.logger import _step, Logger
from utils.screenshot import Screenshot


class Page(object):
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.timeout = config.BROWSER_TIMEOUT
        self.locator = PageLocators

    @allure.step('Finding {locator} on the page')
    def find_element(self, *locator):
        return self.driver.find_element(*locator)

    @allure.step('Checking {locator} whether exists on the page')
    def is_element_exists(self, *locator):
        try:
            self.driver.find_element(*locator)
        except NoSuchElementException:
            return False
        return True

    @_step
    @allure.step('Opening the page')
    def open_page(self, url='', is_overwrite=False, wait_element=None):
        if is_overwrite:
            self.driver.get(url)
        else:
            self.driver.get(f'{self.base_url}{url}')
        if wait_element is not None:
            self.wait_element_to_be_visible(*wait_element)

    @allure.step('Getting title of the page')
    def get_title(self):
        return self.driver.title

    @allure.step('Getting url of the page')
    def get_url(self):
        return self.driver.current_url

    @allure.step('Moving mouse to {locator} on the page')
    def hover(self, *locator):
        element = self.find_element(*locator)
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

    @allure.step('Inputting text to {locator} on the page')
    def input_text(self, text, *locator, is_overwrite=False):
        self.wait_element_to_be_clickable(*locator)
        if is_overwrite:
            self.find_element(*locator).send_keys(Keys.CONTROL + 'a')
            self.find_element(*locator).send_keys(Keys.DELETE)
        self.find_element(*locator).send_keys(text)

    @allure.step('Clicking {locator} on the page')
    def click(self, *locator, timeout: int = None):
        self.wait_element_to_be_clickable(*locator, timeout=timeout)
        self.find_element(*locator).click()

    @allure.step('Right clicking {locator} on the page')
    def right_click(self, *locator):
        self.wait_element_to_be_clickable(*locator)
        element = self.find_element(*locator)
        right_click = ActionChains(self.driver).context_click(element)
        right_click.perform()

    @allure.step('Checking {locator} whether clickable on the page')
    def is_element_clickable(self, *locator):
        cursor = self.find_element(*locator).value_of_css_property("cursor")
        if cursor == "pointer":
            return True
        else:
            return False

    @allure.step('Scrolling page {direction}')
    def scroll_page(self, direction):
        html = self.find_element(*self.locator.html)
        if direction == 'up':
            html.send_keys(Keys.CONTROL + Keys.HOME)
        elif direction == 'down':
            html.send_keys(Keys.END)

    def wait_element(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            Logger().error(f'* Element not found within {self.timeout} seconds! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not found')

    def wait_element_to_be_clickable(self, *locator, timeout: int = None):
        if not timeout:
            timeout = self.timeout
        try:
            WebDriverWait(self.driver, timeout=timeout).until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            Logger().error(f'* Element not clickable within {timeout} seconds! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not found')

    def wait_element_to_be_visible(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            Logger().error(f'* Element not visible within {self.timeout} seconds! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not found')

    def wait_element_to_be_invisible(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            Logger().error(f'* Element not invisible within {self.timeout} seconds! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not disappeared')

    def wait_text_to_be_display(self, text, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.text_to_be_present_in_element(locator, text))
        except TimeoutException:
            Logger().error(f'* {text} not display within {self.timeout} seconds! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{text} not display')

    def wait_url_changed_to(self, url):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.url_contains(url))
        except TimeoutException:
            Logger().error(
                f'* URL not changed to {url} within {self.timeout} seconds! --> current URL is {self.get_url()}')
            Screenshot.take_screenshot(self.driver, f'url not changed to {url}')

    def wait_frame_to_be_visible(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.frame_to_be_available_and_switch_to_it(locator))
        except TimeoutException:
            Logger().error(f'* Frame not visible within {self.timeout} seconds! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not found')

    def wait_element_to_be_visible_in_frame(self, frame_locator, element_locator):
        frame = self.find_element(*frame_locator)
        self.driver.switch_to.frame(frame)
        self.wait_element_to_be_visible(*element_locator)

    def wait_file_presence(self, file_path):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(lambda driver: os.path.exists(file_path))
        except TimeoutException:
            Logger().error(f'* {file_path} not appear within {self.timeout} seconds!')

    @_step
    @allure.step('Wait for download')
    def wait_for_download_completion(self, file_path: Path, file_extension=None, timeout=500):
        if file_extension is None:
            file_name = file_path.name
            download_folder = file_path.parent
        else:
            file_name = file_extension
            download_folder = file_path
        start_time = time.time()
        while time.time() - start_time < timeout:
            part_files = [f for f in os.listdir(download_folder) if (f.endswith('.part') or f.endswith('.crdownload'))]
            if part_files:
                time.sleep(1)
                continue
            target_files = [f for f in os.listdir(download_folder) if f.endswith(file_name)]
            if target_files:
                download_file = os.path.join(download_folder, target_files[0])
                while time.time() - start_time < timeout:
                    initial_size = os.path.getsize(download_file)
                    time.sleep(1)
                    current_size = os.path.getsize(download_file)
                    if current_size != 0 and current_size == initial_size:
                        return
            time.sleep(1)
        error_info = f'Download did not complete within the specified timeout seconds: {timeout}'
        Logger().error(error_info)
        raise TimeoutError(error_info)

    def add_timestamp(self, file_path: Path):
        file_path.replace(Path(file_path.parent, f'{file_path.stem}_{config.CST_NOW_STR}{file_path.suffix}'))
