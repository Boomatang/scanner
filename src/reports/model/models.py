from datetime import datetime
from pony.orm import *

from src.reports.utils import Severity

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
    project_name = Optional(str)
    branch = Optional(str)
    tag = Optional(str)
    issue_opened_scan_id = Optional(int)
    issue_opened_scan_date = Optional(datetime)
    issue_fixed_scan_id = Optional(int)
    issue_fixed_scan_date = Optional(datetime)
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
    project = Required('Project')
    jira = Optional('Jira')


class Record(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Required(datetime)
    severity_high = Optional(int, default=0)
    severity_medium = Optional(int, default=0)
    severity_low = Optional(int, default=0)


class OverviewReport(Record):
    project_reports = Set('ProjectReport')

    def compile_totals(self):
        for report in self.project_reports:
            self.severity_high += report.severity_high
            self.severity_medium += report.severity_medium
            self.severity_low += report.severity_low

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
        elif out > 0:
            out = f"+{out}"

        return out

    def projects_with_change(self, last_report):
        output = {'increase': [], 'decrease': []}
        for project in self.project_reports:
            try:
                last_project = last_report.project_reports.select(
                    lambda lp: lp.project == project.project).first()
                if project.overall_change(last_project) > 0:
                    output['increase'].append(project.name)
                elif project.overall_change(last_project) < 0:
                    output['decrease'].append(project.name)
            except AttributeError as err:
                pass
        return output


class ProjectReport(Record):
    overview_report = Optional(OverviewReport)
    project = Required('Project')

    def overall_change(self, last_project):
        return self.sum_all() - last_project.sum_all()

    def sum_all(self):
        return self.severity_high + self.severity_medium + self.severity_low


class Project(db.Entity):
    id = PrimaryKey(int, auto=True)
    project = Optional(str)
    project_id = Optional(int)
    status = Optional(str, default="New")
    vulnerabilities = Set(Vulnerability)
    project_reports = Set(ProjectReport)
    jiras = Set('Jira')

    def latest_report(self):
        return self.project_reports.select().sort_by(desc(ProjectReport.date)).first()


class Jira(db.Entity):
    id = PrimaryKey(int, auto=True)
    jira = Optional(str)
    link = Optional(str)
    vulnerabilities = Set(Vulnerability)
    project = Required(Project)
