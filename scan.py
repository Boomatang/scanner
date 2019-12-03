import subprocess

from ults import write_status, get_message, SCAN_FILE


def do_scan_work(item):
    data_message = ''
    data_message += run_scan(item)
    write_status(item['name'], item['location'], data_message, SCAN_FILE)


def run_scan(data):
    message = ""
    for project in data['projects']:
        print(f"Scanning project {project} in {data['location']}")
        scan = subprocess.run(["srcclr", "scan", project], capture_output=True)
        message += get_message(scan, f"Scan data for {data['name']} -- {project}")

    return message