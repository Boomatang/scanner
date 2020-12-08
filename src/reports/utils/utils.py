import os
from datetime import datetime
from subprocess import call


def int_check(value):
    if type(value) == int:
        return value
    else:
        return None


def convert_to_datetime(date_string):
    if len(date_string) == 0:
        return None
    try:
        return datetime.strptime(date_string, '%d %b %Y %H:%M%p %Z')
    except ValueError:
        return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f%z')


def is_public(value):
    if value == "Public Disclosure":
        return True
    else:
        return False


# define clear function
def clear():
    # check and make call for specific operating system
    _ = call('clear' if os.name =='posix' else 'cls')
