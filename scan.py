import subprocess
import threading
from pathlib import Path

from ults import write_status, get_message, SCAN_FILE

scan_lock = threading.Lock()


def do_scan_work(item):
    data_message = ''
    data_message += run_scan(item)
    scan_lock.acquire()
    write_status(item['name'], item['location'], data_message, SCAN_FILE)
    scan_lock.release()


def run_scan(data):
    message = ""
    for project in data['projects']:
        path = Path(data['location'], project)
        print(f"Scanning project {project} in {data['location']}")
        scan = subprocess.run(["srcclr", "scan", str(path)], capture_output=True)
        message += get_message(scan, f"Scan data for {data['name']} -- {project}")
        print(f"\nCOMPLETE --> Scanning project {project} in {data['location']}")

    return message

