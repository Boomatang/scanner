from datetime import datetime
from pony.orm import *

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


class Report(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Optional(datetime)
    total_open = Optional(int)
    new_open = Optional(int)
    new_closed = Optional(int)
    severity_high = Optional(int)
    severity_medium = Optional(int)
    severity_low = Optional(int)
