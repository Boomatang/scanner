from datetime import datetime

from pony.orm import desc

from src.reports.model import Report, db_session, db, Vulnerability
from src.reports.utils import Issue, Severity


def find_new_open_vulnerability_after_date(date):
    vs = Vulnerability.select(lambda v: v.issue_opened_scan_date > date)
    print(f"new open issues {len(vs)}")
    return len(vs)


def find_new_closed_vulnerability_after_date(date):
    vs = Vulnerability.select(lambda v: v.issue_fixed_scan_date > date)
    print(f"new closed issues {len(vs)}")
    return len(vs)


def find_open_vulnerabilities(severity=None):
    if severity is None:
        vs = Vulnerability.select(lambda v: v.status == Issue.open)
        print(f"total open issues {len(vs)}")
    else:
        vs = Vulnerability.select(lambda v: v.status == Issue.open and v.severity == severity)
        print(f"severity level {severity} open issues {len(vs)}")
    return len(vs)


@db_session
def run():
    report = Report.select().sort_by(desc(Report.date)).first()
    if report is not None:
        opened = find_new_open_vulnerability_after_date(report.date)
        closed = find_new_closed_vulnerability_after_date(report.date)
    else:
        opened = 0
        closed = 0
    total = find_open_vulnerabilities()
    high = find_open_vulnerabilities(Severity.high)
    medium = find_open_vulnerabilities(Severity.medium)
    low = find_open_vulnerabilities(Severity.low)
    Report(total_open=total,
           new_open=opened,
           new_closed=closed,
           severity_high=high,
           severity_medium=medium,
           severity_low=low,
           date=datetime.now())
    db.commit()

    print()
    if report is not None:
        print(f"Change in high: {high-report.severity_high}")
        print(f"Change in medium: {medium-report.severity_medium}")
        print(f"Change in low: {low-report.severity_low}")
    else:
        print("No previous report to compare with")
