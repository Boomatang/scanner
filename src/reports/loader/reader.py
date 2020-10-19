import csv
import os
from pathlib import Path

from src.reports.model.models import save_file_contents_to_db


def load_csv_data(csv_folder):
    for root, dirs, files in os.walk(csv_folder):
        print(f"files : {files}")
        for csvfile in files:
            path = Path(root, csvfile)
            if path.suffix in ['.csv']:
                print(f"\nWorking on file {csvfile}")
                read_csv(path)


def read_csv(path):
    with open(path, encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        save_file_contents_to_db(reader)