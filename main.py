from git import do_git_work
from scan import do_scan_work
from ults import start_files, get_data, change_working_dir

project_list = []
DATA_FILE = "data/repos.json"


def main():
    start_files()
    print("Load data from file")
    data = get_data(DATA_FILE)
    for item in data:
        run(item)
    print("All scans complete")


def run(item):
    print(f"Working on {item['name']}")
    change_working_dir(item)
    do_git_work(item)
    do_scan_work(item)


if __name__ == "__main__":
    main()
