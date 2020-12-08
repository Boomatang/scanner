import os
from pathlib import Path

from src.reports import loader, next, utils
from src.reports.model import connect_to_database, Project, db, db_session
from src.scanner.ults import get_data

from bullet import Bullet

dev = False
# DATA_FILE = "data/sample-repos.json"
DATA_FILE = os.environ.get("SC_REPO_CONFIG") or "data/sample-repos.json"
print("Running reports")
data = get_data(DATA_FILE)
data = data['reports']
connect_to_database(Path(os.getcwd(), data['database']))

step1 = 'Load scan csv files'
step2 = 'Manage new projects'
step3 = 'Generate Report'
EXIT = "Quit"

cli = Bullet(prompt="Select task", choices=[step1, step2, step3, EXIT])

if dev:
    next.run()

    exit(0)

# Cli loop
while True:
    utils.clear()
    result = cli.launch()
    if result is step1:
        loader.run(data['csvDir'])
    elif result is step2:
        next.project_status()
    elif result is step3:
        next.run()
    elif result is EXIT:
        exit(0)

