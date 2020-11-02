from datetime import datetime

from pony.orm import desc

from src.reports.model import Report, db_session, db, Severity


@db_session
def run():
    last_report = Report.select().sort_by(desc(Report.date)).first()

    current_report = Report(date=datetime.now())
    db.commit()
    if last_report is not None:
        current_report.config(last_report.date)
    else:
        current_report.config()

    print()
    print_summary_report(current_report, last_report)


def print_summary_report(current_report, last_report):
    try:
        if last_report is not None:
            print(f"Change in high: {current_report.severity_high-last_report.severity_high}")
            print(f"Change in medium: {current_report.severity_medium-last_report.severity_medium}")
            print(f"Change in low: {current_report.severity_low-last_report.severity_low}")
        else:
            print("No previous report to compare with")

        print(f"""
Summary

Vulnerability Severity: High: {current_report.severity_high} ( {current_report.level_diff(last_report, Severity.high)} )
Vulnerability Severity: Medium: {current_report.severity_medium} ( {current_report.level_diff(last_report, Severity.high)} )
Vulnerability Severity: Low: {current_report.severity_low} ( {current_report.level_diff(last_report, Severity.high)} )
        """, flush=True)
    except TypeError as err:
        print('lol')
        print(err)
