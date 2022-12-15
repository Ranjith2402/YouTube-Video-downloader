import os


def delete_log_file():
    os.remove('error log/error.txt')


def create_file(text):
    cwd = os.getcwd()
    try:
        os.chdir('Error log')
    except FileNotFoundError:
        os.mkdir('Error log')
        os.chdir("error log")
    try:
        with open('error.txt', 'a+') as file:
            file.write(text)
        os.chdir(cwd)
        return True
    except PermissionError:
        return False


def check_log_file(path=None):
    try:
        if path is None:
            return 'error.txt' in os.listdir('error log/')
        return 'error.txt' in os.listdir(path)
    except FileNotFoundError:
        # print('error')
        return False
