import datetime
import os
import re
from typing import Union

strf_format = "'%d/%m/%Y_%H:%M:%S'"
strf_format_re = r'Error file on \d*/\d*/\d*_\d*:\d*:\d*\.txt'


def delete_log_file(file):
    os.remove(f'error log/{file}')


def create_file(text):
    cwd = os.getcwd()
    try:
        os.chdir('Error log')
    except FileNotFoundError:
        os.mkdir('Error log')
        os.chdir("error log")
    try:
        with open(f"Error file on {datetime.datetime.now().strftime(strf_format)}.txt", 'w+') as file:
            file.write(text)
        os.chdir(cwd)
        return True
    except PermissionError:
        os.chdir(cwd)
        return False


def check_log_file(path=None) -> Union[list, bool]:
    try:
        if path is None:
            return [file for file in os.listdir('error log/') if re.search(strf_format_re, file)]
        return 'error.txt' in os.listdir(path)
    except FileNotFoundError:
        # print('error')
        return False
