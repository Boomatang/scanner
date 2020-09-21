import shutil
import subprocess

from pathlib import Path

from ults import get_message


def workaround_npm_cache(raw_data):
    message = ""
    reset = False
    for data in raw_data:
        if is_npm(data):
            reset = True
            for project in data['projects']:
                path = Path(data['location'], project)
                remove_node_modules(path)

    if reset:
        message += reset_npm_cache()

    if len(message) < 1:
        return "No npm projects found"
    else:
        return message


def remove_node_modules(path):
    dir = Path(path, 'node_modules')
    print("Checking node_modules folder")
    if dir.exists():
        print(f"Removing node_modules folder from {path}")
        shutil.rmtree(dir)


def reset_npm_cache():

    print("Resetting NPM cache with force")
    output = subprocess.run(['npm', 'cache', 'clean', '--force'], capture_output=True)
    message = get_message(output, f"Resetting NPM cache with force")

    return message


def is_npm(data):
    try:
        if data['npm']:
            return True
        else:
            return False
    except KeyError:
        return False
