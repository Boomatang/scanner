#!/usr/bin/env python
import os
from pathlib import Path

from src.reports import loader, next
from src.model import connect_to_database, manage_new_projects_text
from src.scanner.ults import get_data

from bullet import Bullet

dev = False
# DATA_FILE = "data/sample-repos.json"
DATA_FILE = os.environ.get("SC_REPO_CONFIG") or "data/sample-repos.json"
print("Running reports")
data = get_data(DATA_FILE)
data = data['reports']
connect_to_database(Path(os.getcwd(), data['database']))

if dev:
    print(manage_new_projects_text())

    exit(0)

# Cli loop
while True:
    step1 = 'Load scan csv files'
    step2 = manage_new_projects_text()
    step3 = 'Generate Report'
    EXIT = "Quit"
    print()
    cli = Bullet(prompt="Select task", choices=[step1, step2, step3, EXIT])
    result = cli.launch()
    if result is step1:
        loader.run(data['csvDir'])
    elif result is step2:
        next.project_status()
    elif result is step3:
        next.run()
    elif result is EXIT:
        exit(0)

