import queue
import threading
import os

from src.scanner.git import do_git_work, workaround_git_stash
from src.scanner.gradle import gradle_clean
from src.scanner.mvn import mvn_clean
from src.scanner.npm import workaround_npm_cache
from src.scanner.scan import do_scan_work
from src.scanner.ults import start_files, get_data, change_working_dir

project_list = []
DATA_FILE = os.environ.get("SC_REPO_CONFIG") or "data/sample-repos.json"
# DATA_FILE = "data/sample-repos.json"
WORKER_THREADS = 8
task_queue = queue.Queue()
threads = []


def main():
    start_files()
    print("Load data from file")
    data = get_data(DATA_FILE)
    data = data['repos']
    workaround_npm_cache(data)
    workaround_git_stash(data)
    mvn_clean(data)
    gradle_clean(data)
    run_scans(data)
    print("All scans complete")


def run(item):
    print(f"Working on {item['name']}")
    change_working_dir(item)
    do_git_work(item)
    do_scan_work(item)


def worker():
    while True:
        item = task_queue.get()
        if item is None:
            break
        run(item)
        task_queue.task_done()


def run_scans(data):
    for _ in range(WORKER_THREADS):
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    for item in data:
        task_queue.put(item)

    # block until all tasks are done
    task_queue.join()

    # stop workers
    for _ in range(WORKER_THREADS):
        task_queue.put(None)
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
