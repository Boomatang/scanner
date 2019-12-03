import subprocess
import threading

from ults import write_status, get_message, DotDict, GIT_FILE
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
    # checkout = subprocess.run(['git', 'checkout', 'master'], capture_output=True)
    # checkout_message = get_message(checkout, "Git Checkout Status")
    # data_message += checkout_message
    # data_message += "\n"

    pull = subprocess.run(['git', 'pull'], capture_output=True)
    pull_message = get_message(pull, "Git Pull Status")
    data_message += pull_message

    return data_message


def remove_repo_tags(data):
    print(f"Removing repo tags {data['location']}")
    messages = ''
    errors = ''
    tags = subprocess.run(['git', 'tag', '-l'], capture_output=True)
    tags = tags.stdout.decode("utf-8")
    tags = tags.split('\n')
    for tag in tags:
        if len(tag) > 0:
            tag_remove = subprocess.run(['git', 'tag', '-d', tag], capture_output=True)

            if len(tag_remove.stdout) > 0:
                messages += tag_remove.stdout.decode('utf-8')

            if len(tag_remove.stderr) > 0:
                errors += tag_remove.stderr.decode('utf-8')

    return get_message(DotDict({'stdout': messages, 'stderr': errors}), "Git Tag Remove")