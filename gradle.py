import os
import subprocess

from ults import get_message, get_project_path


def gradle_clean(data):
    message = ''
    print("Starting to clean gradle projects")
    current_dir = os.getcwd()
    print(current_dir)

    for entry in data:
        if is_gradle(entry):
            print(f"Running ./gradlew clean on {entry['name']}")
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
        message += run_gradle_clean(path)
    return message


def run_gradle_clean(path):
    """Changes to give path and `mvn clean`"""
    os.chdir(path)
    output = subprocess.run(['./gradlew', 'clean'], capture_output=True)
    message = get_message(output, f"Output from `./gradlew clean` in {path}")

    return message


def is_gradle(data):
    try:
        if data['gradle']:
            return True
        else:
            return False
    except KeyError:
        return False
