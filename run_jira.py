import os
from pathlib import Path

from bullet import Bullet

from src.jira import overview, add_jiras, menu_jira_table, current_jiras_table
from src.model import connect_to_database
from src.scanner.ults import get_data
from src.utils import Severity

DATA_FILE = "data/sample-repos.json"
# DATA_FILE = os.environ.get("SC_REPO_CONFIG") or "data/sample-repos.json"
print("Running reports")
data = get_data(DATA_FILE)
data = data['reports']
connect_to_database(Path(os.getcwd(), data['database']))

# overview()

while True:
    step1 = 'Add JIRA\'s'
    jira_high_severity = menu_jira_table(text="List high severity JIRA's: ", severity=Severity.high)
    jira_all = menu_jira_table(text="List all JIRA's: ")
    EXIT = "Quit"
    print()
    overview()
    print()
    cli = Bullet(prompt="Select task", choices=[step1, jira_high_severity, jira_all, EXIT])
    result = cli.launch()
    print()
    if result is step1:
        add_jiras()
    elif result is jira_high_severity:
        current_jiras_table(severity=Severity.high)
        print()
        input("Return to menu")
    elif result is jira_all:
        current_jiras_table()
        print()
        input("Return to menu")
    elif result is EXIT:
        exit(0)
