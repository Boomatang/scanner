import os
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
                package_lock_action(data, path)

    if reset:
        message += reset_npm_cache()

    if len(message) < 1:
        return "No npm projects found"
    else:
        return message


def package_lock_action(data, path):
    try:
        if data['remove_package_lock']:
            remove_package_lock(path)
    except KeyError:
        pass


def remove_package_lock(path):
    package_lock = Path(path, 'package-lock.json')
    print('Checking for package lock')
    if package_lock.exists():
        print(f'removing {package_lock}')
        os.remove(package_lock)


def remove_node_modules(path):
    node_modules = Path(path, 'node_modules')
    print("Checking node_modules folder")
    if node_modules.exists():
        print(f"Removing node_modules folder from {path}")
        shutil.rmtree(node_modules)


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
