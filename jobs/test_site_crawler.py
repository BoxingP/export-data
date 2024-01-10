import ast

import allure
import pandas as pd
import pytest

from pages.locators import LoginPageLocators, HomePageLocators
from pages.login_page import LoginPage
from pages.user_page import UserPage
from utils.config import config
from utils.excel_file import ExcelFile
from utils.utils import get_base_url_by_job_name, get_current_function_name


@pytest.mark.usefixtures('setup')
class TestSiteCrawler:
    reruns = config.JOB_RERUNS
    reruns_delay = config.JOB_RERUNS_DELAY

    def get_email_list(self):
        data_path = config.EMAIL_LIST_FILE_PATH
        df = ExcelFile(data_path.name, data_path).import_excel_to_dataframe()
        email_list = df['Email'].tolist()
        return email_list

    def generate_report(self, device_list):
        df = pd.DataFrame(device_list)
        column_mapping = config.DEVICE_COLUMN_MAPPING
        df.rename(columns=column_mapping, inplace=True)
        email_column = df.pop('Email')
        df.insert(0, 'Email', email_column)

        os_to_exclude = config.DEVICE_OS_TO_EXCLUDE
        df_filtered = df[~df['OS'].isin(os_to_exclude)]

        report_path = config.DEVICE_LIST_FILE_PATH
        with ExcelFile(report_path.name, report_path) as excel:
            excel.export_dataframe_to_excel(df_filtered, 'device_list', set_width_by_value=True)

    @pytest.mark.usefixtures('screenshot_on_failure')
    @pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
    @allure.title('Download mem report test')
    @allure.description('This is test of download mem report')
    def test_download_mem_report(self):
        base_url = get_base_url_by_job_name(config.JOB_LIST, get_current_function_name())
        user_page = UserPage(self.driver, base_url)
        user_page.open_page(wait_element=LoginPageLocators.msft_logo_img)
        login_page = LoginPage(self.driver, base_url)
        login_page.login(user='mem', wait_element=HomePageLocators.msft_user_info_button)
        device_list = []
        email_list = self.get_email_list()
        for email in email_list:
            user_page.open_page(url='#view/Microsoft_AAD_UsersAndTenants/UserManagementMenuBlade/~/AllUsers')
            device_info = user_page.get_device_info(email=email)
            device_list.extend(device_info)
        self.generate_report(device_list)
