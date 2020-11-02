from datetime import datetime
from pony.orm import *

from src.reports.utils import Issue, Severity

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

    @classmethod
    def severity_issues(cls, severity, project_id=None):
        if project_id is not None:
            return cls.select(lambda v: v.status == Issue.open
                              and v.project_id == project_id
                              and v.severity == severity).count()
        else:
            return cls.select(lambda v: v.status == Issue.open
                              and v.severity == severity).count()

    @classmethod
    def new_open_vulnerability_after_date(cls, date=None, project_id=None):
        if date is not None:
            if project_id is not None:
                vs = cls.select(lambda v: v.issue_opened_scan_date > date and v.project_id == project_id)
            else:
                vs = cls.select(lambda v: v.issue_opened_scan_date > date)
            return len(vs)
        else:
            return 0

    @classmethod
    def new_closed_vulnerability_after_date(cls, date=None, project_id=None):
        if date is not None:
            if project_id is not None:
                vs = cls.select(lambda v: v.issue_fixed_scan_date > date and v.project_id == project_id)
            else:
                vs = cls.select(lambda v: v.issue_fixed_scan_date > date)
            return len(vs)
        else:
            return 0

    @classmethod
    def open_vulnerabilities(cls, severity=None, project_id=None):
        if severity is None:
            if project_id is not None:
                return cls.select(lambda v: v.status == Issue.open
                                                       and v.project_id == project_id).count()
            else:
                return cls.select(lambda v: v.status == Issue.open).count()
        else:
            return cls.severity_issues(severity, project_id)


class Record(db.Entity):
    id = PrimaryKey(int, auto=True)
    new_open = Optional(int)
    new_closed = Optional(int)
    total_open = Optional(int)
    severity_high = Optional(int)
    severity_medium = Optional(int)
    severity_low = Optional(int)

    def config(self, date=None, project_id=None):
        self.new_closed = Vulnerability.new_closed_vulnerability_after_date(date, project_id)
        self.new_open = Vulnerability.new_open_vulnerability_after_date(date, project_id)
        self.total_open = Vulnerability.open_vulnerabilities(project_id=project_id)
        self.severity_high = Vulnerability.open_vulnerabilities(severity=Severity.high, project_id=project_id)
        self.severity_medium = Vulnerability.open_vulnerabilities(severity=Severity.medium, project_id=project_id)
        self.severity_low = Vulnerability.open_vulnerabilities(severity=Severity.low, project_id=project_id)


class Report(Record):
    date = Optional(datetime)
    projects = Set('Project')

    def config(self, date=None, project_id=None):
        super(Report, self).config(date, project_id)
        self.add_projects()
        for project in self.projects:
            project.config(date, project.project_id)

    def add_projects(self):
        print("Adding Projects")
        issues = Vulnerability.select(lambda v: v.status == Issue.open)
        for issue in issues:
            project = self.projects.filter(lambda p: p.project_id == issue.project_id)
            if len(project) == 0:
                self.projects.create(project_id=issue.project_id, name=issue.project)
        db.commit()

    def level_diff(self, last_report, level):
        if last_report is None:
            return "na"
        if level == Severity.high:
            out = self.severity_high - last_report.severity_high
        elif level == Severity.medium:
            out = self.severity_medium - last_report.severity_medium
        elif level == Severity.low:
            out = self.severity_low - last_report.severity_low
        else:
            out = "na"

        if out == 0:
            out = "--"

        return out


class Project(Record):
    name = Optional(str)
    project_id = Optional(int)
    report = Required(Report)
