import os

import pytest

from utils.config import config
from utils.cron_selector import get_jobs_to_run
from utils.excel_file import ExcelFile
from utils.random_generator import random_browser


def clean_email(email: str):
    return email.lower().strip()


def get_email_list_str():
    data_path = config.EMAIL_LIST_FILE_PATH
    df = ExcelFile(data_path.name, data_path).import_excel_to_dataframe()
    email_list = df['Email'].tolist()
    cleaned_email_list = [clean_email(item) for item in email_list]
    return ','.join(cleaned_email_list)


def main():
    email_list_str = get_email_list_str()

    jobs_to_run = get_jobs_to_run(config.JOB_LIST)
    mem_list = [element for element in jobs_to_run if "mem" in element]
    print(f"Running jobs: {', '.join(mem_list)}")
    if jobs_to_run:
        random_browser()
        pytest.main(
            [f"{os.path.join(os.path.dirname(__file__), 'jobs')}",
             "--dist=loadfile",
             "--order-dependencies",
             f"--alluredir={config.ALLURE_RESULTS_DIR_PATH}",
             '--cache-clear',
             '-k', ' or '.join(mem_list),
             '-s',
             f'--email-list={email_list_str}']
        )


if __name__ == '__main__':
    main()
