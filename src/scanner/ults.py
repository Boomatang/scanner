import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = os.getcwd()
GIT_FILE = "out/git-log.txt"
SCAN_FILE = "out/srcclr-log.txt"


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def today():
    today_date = date.today()
    # dd/mm/YY
    return today_date.strftime("%d/%m/%Y")


def write_status(repo_name, location, meassage, file_name):
    git_file = str(Path(ROOT, file_name))
    spacer = "=" * 10
    header = f"{spacer} {repo_name} {spacer}"
    footer = "=" * len(header)

    with open(git_file, 'a') as gfile:
        gfile.write(f"{header}\n")
        gfile.write(f"{footer}\n\n")
        gfile.write(f"PATH : \n{location}\n")
        gfile.write(f"\n")
        gfile.write(f"{meassage}\n")
        gfile.write(f"{footer}\n\n")


def print_error(*args, **kargs):
    print(*args, file=sys.stderr, **kargs)


def get_message(data, title):
    message = f"> {title}\n\n"
    if type(data) is not DotDict:
        stdout = data.stdout.decode('utf-8')
        error = data.stderr.decode('utf-8')
    else:
        stdout = data.stdout
        error = data.stderr

    if len(stdout) > 0:
        message += f">> Message\n\t{stdout}\n"
    if len(error) > 0:
        # print_error(error)
        message += f">> Error Found\n\t{error}\n"
    return message


def start_files():
    git_file = str(Path(ROOT, GIT_FILE))
    with open(git_file, 'w') as gfile:
        gfile.write(f"Scan Date : {today()}\n\n")

    scan_file = str(Path(ROOT, SCAN_FILE))
    with open(scan_file, 'w') as sfile:
        sfile.write(f"Scan Date : {today()}\n\n")


def get_data(filename):
    data = None
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def change_working_dir(data):
    os.chdir(data['location'])
    print(f"Current working DIR {os.getcwd()}")


def get_project_path(project, root):
    if project == '.':
        return Path(root)
    else:
        return Path(root, project)