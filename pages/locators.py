from selenium.webdriver.common.by import By

from utils.users import User


class PageLocators(object):
    body = (By.XPATH, '//body')
    html = (By.TAG_NAME, 'html')


class HomePageLocators(PageLocators):
    email = (User().get_user('mem'))['email']
    msft_user_info_button = (By.XPATH, f'//div[contains(@title, "{email}")]')


class LoginPageLocators(PageLocators):
    tmo_logo_img = (By.ID, 'bannerLogo')
    sso_username_field = (By.XPATH, '//input[contains(@type, "email")]')
    next_button = (
        By.XPATH, '//input[contains(@type, "submit") and (contains(@value, "Next") or contains(@value, "Yes"))]')
    display_field = (By.ID, 'displayName')
    sso_password_field = (By.XPATH, '//*[@id="lightbox"]//input[contains(@type, "password")]')
    sso_sign_in_button = (By.XPATH, '//*[@id="lightbox"]//input[contains(@value, "Sign in")]')
    stay_signed_in_field = (By.XPATH, '//*[@id="lightbox"]//div[contains(text(), "Stay signed in")]')
    msft_logo_img = (By.XPATH, '//*[@id="lightbox"]/div/img[contains(@class, "logo")]')


class UserPageLocators(PageLocators):
    session_expired_info = (By.XPATH, '//h1[contains(text(),"Session expired")]')
    try_again_button = (By.ID, 'error-page-content-tryagain')
    user_title = (By.XPATH, '//h2[contains(text(),"Users")]')
    users_list = (By.XPATH, '//iframe[contains(@name, "UsersList.ReactView")]')
    search_field = (By.XPATH, '//input[contains(@class,"ms-SearchBox-field")]')
    user_link = (By.XPATH,
                 '((//div[@class="ms-DetailsList-contentWrapper"]//div[@role="presentation" and @class="ms-List-cell"])[1]//a)[1]')
    device_title = (By.XPATH, '//h2/span[contains(text(),"Device")]')
    devices_list = (By.XPATH, '//iframe[contains(@name, "DevicesList.ReactView")]')
    device_row = (By.XPATH, '//div[contains(@class, "ms-DetailsRow-fields")]')
    no_results_info = (By.XPATH, '//label[contains(text(),"No results")]')
    devices_found_info = (By.XPATH, '//div[@role="presentation"]//div[contains(@class, "ms-Shimmer-dataWrapper")]/div')
    device_found_loading_bar = (
        By.XPATH, '//div[@role="presentation"]//div[contains(@class, "ms-Shimmer-shimmerGradient")]')
    users_found_info = (By.XPATH, '//div[contains(@class, "ms-Shimmer-dataWrapper")]/div[@data-testid="resultMessage"]')
    add_filter_loading_bar = (By.XPATH,
                              '//div[@elementtiming and @class and count(@*)=2 and contains(@class, "ms-SearchBox")]/following::div[1]//div[contains(@class, "ms-Shimmer-shimmerWrapper")]')
    user_overview_title = (
        By.XPATH,
        '//h2[contains(text(),",") or contains(text()," ") or contains(text(),"_") or contains(text(),"-") or contains(text(),".")]')
    user_profile = (By.XPATH, '//iframe[contains(@name, "UserProfile.ReactView")]')
    user_email = (
        By.XPATH, '//div[contains(@class, "ms-Persona-details")]/div[contains(@class, "ms-Persona-secondary")]/div')
    home_title = (By.XPATH, '//h2[contains(text(),"Thermo Fisher")]')
