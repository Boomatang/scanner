import queue
import threading

from git import do_git_work
from scan import do_scan_work
from ults import start_files, get_data, change_working_dir

project_list = []
DATA_FILE = "data/repos.json"
WORKER_THREADS = 8
task_queue = queue.Queue()
threads = []


def main():
    start_files()
    print("Load data from file")
    data = get_data(DATA_FILE)
    action(data)
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


def action(data):
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
