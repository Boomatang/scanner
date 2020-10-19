import csv
from datetime import datetime
from pony.orm import *
from pony.orm import db_session

from src.reports.utils.emun import Issue
from src.reports.utils.utils import convert_to_datetime, int_check, is_public

db = Database()


class Vulnerability(db.Entity):
    id = PrimaryKey(int, auto=True)
    issue_id = Optional(int, unique=True)
    ignored = Optional(bool)
    status = Optional(str)
    project_id = Optional(int)
    library = Optional(str)
    version_in_use = Optional(str)
    library_release_date = Optional(datetime)
    package_manager = Optional(str)
    coordinate1 = Optional(str)
    coordinate2 = Optional(str)
    latest_version = Optional(str)
    latest_release_data = Optional(datetime)
    project = Optional(str)
    branch = Optional(str)
    tag = Optional(str)
    issue_opened_scan_id = Optional(int)
    issue_opened_scan_date = Optional(datetime)
    issue_fixed_scan_id = Optional(int)
    issue_fixed_scan_date = Optional(datetime, volatile=True)
    dependency = Optional(str)
    scan = Optional(int)
    scan_date = Optional(datetime)
    vulnerability_id = Optional(int)
    title = Optional(str)
    cvss_score = Optional(float)
    severity = Optional(str)
    cve = Optional(str)
    public_disclosure = Optional(bool)
    disclosure_date = Optional(datetime)
    has_vulnerable_methods = Optional(bool)
    number_of_vulnerable_methods = Optional(int)


class File(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str, unique=True)
    date = Optional(datetime)
    path = Optional(str)


def connect_to_database(database=None):
    print(database)
    db.bind(provider='sqlite', filename=str(database), create_db=True)
    # db.bind(provider='sqlite', filename=':memory:')
    db.generate_mapping(create_tables=True)


def update_resolved_issue_in_db(row, value):
    with db_session:
        value.status = row[Issue.status]
        value.issue_fixed_scan_id = row[Issue.issue_fixed_scan_id]
        value.issue_fixed_scan_date = convert_to_datetime(row[Issue.issue_fixed_scan_date])
        value.scan = row[Issue.scan]
        value.scan_date = convert_to_datetime(row[Issue.scan_date])
        db.commit()


@db_session
def issue_in_db(row):
    value = Vulnerability.get(issue_id=row[Issue.issue_id])
    if value is not None:
        return True
    else:
        return False


@db_session
def save_row_to_db(row):
    entry = Vulnerability()
    entry.issue_id = row['Issue ID']
    entry.ignored = row['Ignored']
    entry.status = row['Status']
    entry.project_id = row['Project ID']
    entry.library = row['Library']
    entry.version_in_use = row['Version in use']
    entry.library_release_date = convert_to_datetime(row['Library release date'])
    entry.package_manager = row['Package manager']
    entry.coordinate1 = row['Coordinate 1']
    entry.coordinate2 = row['Coordinate 2']
    entry.latest_version = row['Latest version']
    entry.latest_release_data = convert_to_datetime(row['Latest release date'])
    entry.project = row['Project']
    entry.branch = row['Branch']
    entry.tag = row['Tag']
    entry.issue_opened_scan_id = row['Issue opened: Scan ID']
    entry.issue_opened_scan_date = convert_to_datetime(row['Issue opened: Scan date'])
    entry.issue_fixed_scan_id = int_check(row['Issue fixed: Scan ID'])
    entry.issue_fixed_scan_date = convert_to_datetime(row['Issue fixed: Scan date'])
    entry.dependency = row['Dependency (Transitive or Direct)']
    entry.scan = row['Scan']
    entry.scan_date = convert_to_datetime(row['Scan date'])
    entry.vulnerability_id = row['Vulnerability ID']
    entry.title = row['Title']
    entry.cvss_score = row['CVSS score']
    entry.severity = row['Severity']
    entry.cve = row['CVE']
    entry.public_disclosure = is_public(row['Public or Veracode Customer Access'])
    entry.disclosure_date = convert_to_datetime(row['Disclosure date'])
    entry.has_vulnerable_methods = row['Has vulnerable methods']
    entry.number_of_vulnerable_methods = row['Number of vulnerable methods']


@db_session
def issue_status_change(row):
    value = Vulnerability.get(issue_id=row[Issue.issue_id])
    if row[Issue.status] != value.status:
        return True
    else:
        return False


def save_file_contents_to_db(reader: csv.DictReader):
    for row in reader:
        if not issue_in_db(row):
            save_row_to_db(row)
        elif issue_status_change(row):
            update_issue_if_required(row)
        else:
            # print("existing issue")
            pass
    db.commit()


@db_session
def update_issue_if_required(row):
    value: Vulnerability = Vulnerability.get(issue_id=row[Issue.issue_id])
    if value.status == Issue.open \
            and row[Issue.status] == Issue.resolved:
        update_resolved_issue_in_db(row, value)
    elif value.issue_opened_scan_id == int(row[Issue.issue_opened_scan_id]):
        print(f"{value.project}: {value.vulnerability_id}: previously updated")
    else:
        print("ERROR")
        print(f"There is some thing else going on here: {value.project}: {value.vulnerability_id}")
        print(f"{value.issue_opened_scan_date} > {convert_to_datetime(row[Issue.issue_opened_scan_date])} : {value.issue_opened_scan_date > convert_to_datetime(row[Issue.issue_opened_scan_date])}")