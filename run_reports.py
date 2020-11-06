import os
from pathlib import Path

from src.reports import loader, next
from src.reports.model import connect_to_database
from src.scanner.ults import get_data

DATA_FILE = "data/sample-repos.json"
print("Running reports")
data = get_data(DATA_FILE)
data = data['reports']
print(data)
connect_to_database(Path(os.getcwd(), data['database']))

loader.run(data['csvDir'])
next.run()
