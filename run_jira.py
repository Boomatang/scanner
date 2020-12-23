import os
from pathlib import Path

from bullet import Bullet

from src.jira import overview, add_jiras
from src.model import connect_to_database
from src.scanner.ults import get_data

DATA_FILE = "data/sample-repos.json"
# DATA_FILE = os.environ.get("SC_REPO_CONFIG") or "data/sample-repos.json"
print("Running reports")
data = get_data(DATA_FILE)
data = data['reports']
connect_to_database(Path(os.getcwd(), data['database']))

# overview()

while True:
    step1 = 'Add JIRA\'s'
    EXIT = "Quit"
    print()
    overview()
    print()
    cli = Bullet(prompt="Select task", choices=[step1, EXIT])
    result = cli.launch()
    if result is step1:
        add_jiras()
    elif result is EXIT:
        exit(0)
