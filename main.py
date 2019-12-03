import queue
import threading

from git import do_git_work
from scan import do_scan_work
from ults import start_files, get_data, change_working_dir

project_list = []
DATA_FILE = "data/repos.json"
num_worker_threads = 2
q = queue.Queue()
threads = []


def main():
    start_files()
    print("Load data from file")
    data = get_data(DATA_FILE)
    # for item in data:
    #     run(item)
    action(data)
    print("All scans complete")


def run(item):
    print(f"Working on {item['name']}")
    change_working_dir(item)
    # do_git_work(item)
    do_scan_work(item)


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        run(item)
        q.task_done()


def action(data):
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for item in data:
        q.put(item)

    # block until all tasks are done
    q.join()

    # stop workers
    for i in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
