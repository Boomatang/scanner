import csv

from pony.orm import db_session

from src.reports.model import db, Vulnerability, Project
from src.reports.utils.emun import Issue, Severity
from src.reports.utils.utils import convert_to_datetime, int_check, is_public


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
def project_in_db(project_id):
    value = Project.get(project_id=project_id)
    if value is not None:
        return True
    else:
        return False


@db_session
def save_row_to_db(row):
    if project_in_db(row['Project ID']):
        project = Project.get(project_id=row['Project ID'])
    else:
        project = Project()
        project.project = row['Project']
        project.project_id = row['Project ID']

    entry = Vulnerability(project=project)
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
    entry.project_name = row['Project']
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


@db_session
def issue_severity_change(row):
    value = Vulnerability.get(issue_id=row[Issue.issue_id])
    if row[Issue.severity] != value.severity and convert_to_datetime(row[Issue.scan_date]) > value.scan_date:
        return True
    else:
        return False


def save_file_contents_to_db(reader: csv.DictReader):
    for row in reader:
        if not issue_in_db(row):
            save_row_to_db(row)
        elif issue_status_change(row) or issue_severity_change(row):
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
    elif row[Issue.severity] != value.severity:
        value.severity = row[Issue.severity]
        value.cvss_score = row[Issue.cvss_score]
        db.commit()
        print("severity updated")

    elif value.issue_opened_scan_id == int(row[Issue.issue_opened_scan_id]):
        print(f"{value.project_name}: {value.vulnerability_id}: previously updated")
    else:
        print("ERROR")
        print(f"There is some thing else going on here: {value.project}: {value.vulnerability_id}")
        print(f"{value.issue_opened_scan_date} > {convert_to_datetime(row[Issue.issue_opened_scan_date])} : "
              f"{value.issue_opened_scan_date > convert_to_datetime(row[Issue.issue_opened_scan_date])}")


def report_entries(project):
    high = 0
    medium = 0
    low = 0

    for vulnerability in project.vulnerabilities:
        if vulnerability.status == "Open":
            if vulnerability.severity == Severity.high:
                high += 1
            elif vulnerability.severity == Severity.medium:
                medium += 1
            elif vulnerability.severity == Severity.low:
                low += 1
    return high, medium, low


@db_session
def manage_new_projects_text():
    output = 'Manage new projects'

    projects = Project.select()

    if projects.filter(status="Skip").count() > 0:
        output += f", Skipped: {projects.filter(status='Skip').count()}"

    if projects.filter(status="New").count() > 0:
        output += f", New: {projects.filter(status='New').count()}"

    return output
