import allure

from pages.locators import LoginPageLocators
from pages.page import Page
from utils.logger import _step
from utils.users import User


class LoginPage(Page):
    def __init__(self, driver, base_url):
        super(LoginPage, self).__init__(driver, base_url)
        self.locator = LoginPageLocators

    @_step
    @allure.step('Login with user: {user}')
    def login(self, user, wait_element=None):
        user = User().get_user(user)
        self.input_text(user['email'], *self.locator.sso_username_field, is_overwrite=True)
        self.click(*self.locator.next_button)
        self.wait_element_to_be_visible(*self.locator.display_field)
        self.input_text(user['password'], *self.locator.sso_password_field)
        self.click(*self.locator.sso_sign_in_button)
        self.wait_element_to_be_visible(*self.locator.stay_signed_in_field)
        self.click(*self.locator.next_button)
        if wait_element:
            self.wait_element_to_be_visible(*wait_element)
