import os
from pathlib import Path

from src.model import Jira, Vulnerability, connect_to_database, db_session, desc, db
from src.scanner.ults import get_data
from src.utils import Severity


def open_issue_no_jiras():
    """return the search results for issues that currently do not have any Jira assigned"""
    issues = Vulnerability.select(lambda v: v.status == "Open" and v.jira is None)
    return issues


def jiras_with_open_issues(severity=None):
    """return the search results for jiras currently with open issues"""
    if severity is None:
        jiras = Jira.select(lambda x: len(x.open_issues()) > 0)
    elif severity == Severity.high:
        jiras = Jira.select(lambda x: len(x.open_high_severity_issues()) > 0)
    else:
        return "Error in set up"
    return jiras


@db_session
def overview():
    print(f"Running JIRA's: {__name__}")
    print(f"Number of open issue without assigned JIRA's: {open_issue_no_jiras().count()}")
    print(f"Number of JIRA's with open issues: {jiras_with_open_issues().count()}")
    print(f"Number of JIRA's with high severity open issues: {jiras_with_open_issues(severity=Severity.high).count()}")


@db_session
def add_jiras():
    """for open issues add the correct jira"""
    # get list of open issues
    issue = open_issue_no_jiras().sort_by(desc(Vulnerability.cvss_score)).first()
    # Display one of the open issues
    print(issue.summary())
    # Ask if ready to add jira number
    value = input("Add jira [yes]: ")
    if value.strip().lower() in ["yes", "y", ""]:
        print("\nAdding jira, All Jiras will be created as uppercase")
        # if yes ask for issue number
        value = input("\nWhat is the jira number: ")
        value = value.strip().upper()
        print(f"Adding \"{issue.title}\" to JIRA \"{value}\"")
        # After getting issue number
        add_issue_to_jira(issue, value)
    if open_issue_no_jiras().count() > 0:
        print()
        print(f"Number of open issue without assigned JIRA's: {open_issue_no_jiras().count()}")
        value = input("Keep adding jira [yes]: ")
        if value.strip().lower() in ["yes", "y", ""]:
            add_jiras()


def add_issue_to_jira(issue, value):
    """
    Checks if jira is existing if so add issue to jira
    Else a new jira is created and the issue is added to that one.
    The same project will be used when adding new issues to existing jiras
    """
    jira = Jira.get(link=value)
    if jira is None:
        # create a new jira in the project for the issue
        jira = Jira(link=value, project=issue.project)
        jira.vulnerabilities.add(issue)
        issue.project.jiras.add(jira)
        db.commit()
    else:
        if jira.project.id != issue.project.id:
            print("Trying to add issue to existing JIRA which belongs to a different project. "
                  "\nPlease check your inputs.")
        else:
            # Then add the issue to the jira
            jira.vulnerabilities.add(issue)
            db.commit()


if __name__ == "__main__":
    DATA_FILE = "../../data/sample-repos.json"
    data = get_data(DATA_FILE)
    data = data['reports']
    location = Path(os.getcwd())
    parents = location.parts[:-2]
    location = Path(*parents, data['database'])
    connect_to_database(location)

    overview()
    add_jiras()
