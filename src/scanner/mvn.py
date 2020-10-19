import os
import subprocess

from src.scanner.ults import get_message, get_project_path


def mvn_clean(data):
    message = ''
    print("Starting to clean mevan projects")
    current_dir = os.getcwd()
    print(current_dir)

    for entry in data:
        if is_mvn(entry):
            print(f"Running mvn clean on {entry['name']}")
            message += clean_projects(entry['projects'], entry['location'])

    os.chdir(current_dir)
    return message


def clean_projects(projects, root):
    message = ''
    for project in projects:
        path = get_project_path(project, root)
        if not path.exists():
            print(f"miss configured project path: {path} ")
            continue
        print(f"starting mvn clean in: {path}")
        message += run_nvm_clean(path)
    return message


def run_nvm_clean(path):
    """Changes to give path and `mvn clean`"""
    os.chdir(path)
    output = subprocess.run(['mvn', 'clean'], capture_output=True)
    message = get_message(output, f"Output from `nvm clean` in {path}")

    return message


def is_mvn(data):
    try:
        if data['mevan']:
            return True
        else:
            return False
    except KeyError:
        return False
