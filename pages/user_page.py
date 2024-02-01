import re

import allure
from bs4 import BeautifulSoup
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.locators import UserPageLocators
from pages.page import Page
from utils.logger import _step
from utils.screenshot import Screenshot


class UserPage(Page):
    def __init__(self, driver, base_url):
        super(UserPage, self).__init__(driver, base_url)
        self.locator = UserPageLocators
        self.custom_timeout = 10

    def wait_element_to_be_visible(self, *locator):
        WebDriverWait(self.driver, timeout=self.custom_timeout).until(EC.visibility_of_element_located(locator))

    def handle_session_expired(self):
        try:
            super().wait_element_to_be_visible(*self.locator.session_expired_info)
            self.click(*self.locator.try_again_button)
            return True
        except NoSuchElementException:
            Screenshot.take_screenshot(self.driver, 'no_such_element')
            return False

    def handle_redirect_homepage(self):
        try:
            super().wait_element_to_be_visible(*self.locator.home_title)
            return True
        except TimeoutException:
            return False

    def wait_title_to_be_visible(self, url, locator, max_retries=6):
        for _ in range(max_retries):
            try:
                self.open_page(url)
                self.wait_element_to_be_visible(*locator)
                return
            except TimeoutException:
                if self.handle_redirect_homepage():
                    continue
                if self.handle_session_expired():
                    continue

    def wait_component(self, component, max_retries=3):
        for _ in range(max_retries):
            try:
                self.wait_title_to_be_visible(url=component['url'], locator=component['title'])
                self.wait_frame_to_be_visible(*component['frame'])
                if 'element' in component:
                    super().wait_element_to_be_visible(*component['element'])
                    return self.find_element(*component['element'])
                if 'input' in component:
                    self.input_text(component['input_content'], *component['input'], is_overwrite=True)
                if 'loading' in component:
                    self.wait_element_to_be_invisible(*component['loading'])
                    return
            except NoSuchElementException:
                continue

    @_step
    @allure.step('Get device info')
    def get_device_info(self, email, user_id):
        device_info = []
        component = {
            'url': f'#view/Microsoft_AAD_UsersAndTenants/UserProfileMenuBlade/~/Devices/userId/{user_id}/hidePreviewBanner~/true',
            'title': self.locator.device_title,
            'frame': self.locator.devices_list,
            'loading': self.locator.device_found_loading_bar
        }
        self.wait_component(component)
        if self.is_found(self.locator.devices_found_info, '0 devices found'):
            super().wait_element_to_be_visible(*self.locator.device_row)
            elements = self.driver.find_elements(*self.locator.device_row)
            for element in elements:
                html_code = element.get_attribute('outerHTML')
                device_detail = self.get_device_detail(html_code)
                device_info.append(device_detail)
        if device_info:
            for device in device_info:
                device['Email'] = email
        return device_info

    def is_found(self, locator, not_found_info):
        try:
            self.wait_element_text_to_be_changed(locator, not_found_info)
            return True
        except TimeoutException:
            try:
                super().wait_element_to_be_visible(*self.locator.no_results_info)
                return False
            except NoSuchElementException as exception:
                Screenshot.take_screenshot(self.driver, 'no_such_element')

    def element_text_changed(self, locator, expected_text):
        element = self.find_element(*locator)
        current_text = element.text.strip()
        return current_text and current_text != expected_text

    def wait_element_text_to_be_changed(self, locator, expected_text):
        super().wait_element_to_be_visible(*locator)
        WebDriverWait(self.driver, timeout=self.custom_timeout).until(
            lambda x: self.element_text_changed(locator, expected_text))

    @_step
    @allure.step('Get user id')
    def get_user_id(self, email, max_retries=2):
        for _ in range(max_retries):
            user_id = self.extract_user_id(email)
            if user_id is None or email == self.extract_email(user_id):
                return user_id
        return None

    @_step
    @allure.step('Extract user id')
    def extract_user_id(self, email):
        self.search_user(email)
        if self.is_found(self.locator.users_found_info, '0 users found'):
            super().wait_element_to_be_visible(*self.locator.user_link)
            link = self.find_element(*self.locator.user_link).get_attribute('href')
            user_id_pattern = re.compile(r'userId/([0-9a-fA-F-]+)')
            match = user_id_pattern.search(link)
            if match:
                user_id = match.group(1)
                return user_id
        else:
            return None

    @_step
    @allure.step('Search user')
    def search_user(self, email):
        component = {
            'url': '#view/Microsoft_AAD_UsersAndTenants/UserManagementMenuBlade/~/AllUsers',
            'title': self.locator.user_title,
            'frame': self.locator.users_list,
            'input': self.locator.search_field,
            'input_content': email,
            'loading': self.locator.add_filter_loading_bar
        }
        self.wait_component(component)

    def get_device_detail(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        details_cells = soup.find_all('div', class_='ms-DetailsRow-cell')
        data_dict = {}
        for cell in details_cells:
            key = cell.get('data-automation-key')
            value = cell.get_text(strip=True)
            data_dict[key] = value
        return data_dict

    @_step
    @allure.step('Extract email')
    def extract_email(self, user_id):
        component = {
            'url': f'#view/Microsoft_AAD_UsersAndTenants/UserProfileMenuBlade/~/overview/userId/{user_id}',
            'title': self.locator.user_overview_title,
            'frame': self.locator.user_profile,
            'element': self.locator.user_email
        }
        return self.wait_component(component).text.lower().strip()
