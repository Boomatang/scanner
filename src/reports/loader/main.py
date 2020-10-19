import os
from pathlib import Path

from src.reports.model.models import connect_to_database
from src.reports.loader.reader import load_csv_data
from src.scanner.ults import get_data

DATA_FILE = "data/sample-repos.json"


def run():
    print("Running reports")
    data = get_data(DATA_FILE)
    data = data['reports']
    print(data)
    connect_to_database(Path(os.getcwd(), data['database']))
    load_csv_data(data['csvDir'])


if __name__ == "__main__":
    run()
