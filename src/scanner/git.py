import subprocess
import threading

from src.scanner.ults import write_status, get_message, DotDict, GIT_FILE

git_lock = threading.Lock()


def do_git_work(item):
    data_message = ''
    data_message += update_repo(item)
    data_message += remove_repo_tags(item)
    git_lock.acquire()
    write_status(item['name'], item['location'], data_message, GIT_FILE)
    git_lock.release()


def update_repo(data):
    data_message = ''
    print(f"Update repo {data['location']}")
    pull = subprocess.run(['git', '-C', data['location'], 'pull'], capture_output=True)
    pull_message = get_message(pull, "Git Pull Status")
    data_message += pull_message

    return data_message


def remove_repo_tags(data):
    print(f"Removing repo tags {data['location']}")
    messages = ''
    errors = ''
    tags = subprocess.run(['git', '-C', data['location'], 'tag', '-l'], capture_output=True)
    tags = tags.stdout.decode("utf-8")
    tags = tags.split('\n')
    for tag in tags:
        if len(tag) > 0:
            tag_remove = subprocess.run(['git', '-C', data['location'], 'tag', '-d', tag], capture_output=True)

            if len(tag_remove.stdout) > 0:
                messages += tag_remove.stdout.decode('utf-8')

            if len(tag_remove.stderr) > 0:
                errors += tag_remove.stderr.decode('utf-8')

    return get_message(DotDict({'stdout': messages, 'stderr': errors}), "Git Tag Remove")


def git_stash(data):
    print(f"Stashing changes at {data['name']}")
    messages = ''
    errors = ''
    stash = subprocess.run(['git', '-C', data['location'], 'stash'], capture_output=True)
    if len(stash.stdout) > 0:
        messages += stash.stdout.decode('utf-8')

    if len(stash.stderr) > 0:
        errors += stash.stderr.decode('utf-8')

    return get_message(DotDict({'stdout': messages, 'stderr': errors}), "Git Stash")


def workaround_git_stash(raw_data):
    result = ''
    for data in raw_data:
        if 'git stash' in data and data['git stash']:
            print(f"{data['name']} ->> git stash work around")
            result += git_stash(data)
    return result
