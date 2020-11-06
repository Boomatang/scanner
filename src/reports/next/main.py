from datetime import datetime

from pony.orm import desc

from src.reports.model import Report, db_session, db, Severity
import subprocess

mailing_list = 'Source Clear Scans <Source Clear Scans>'


def create_email_with_thunderbird(to, subject, body):
    output = subprocess.run(["thunderbird", "-compose", f"to={to},subject={subject},body={body}"], capture_output=True)
    print(output)


def get_date():
    now = datetime.now()
    return now.strftime('%d/%m/%Y')


@db_session
def run():
    last_report = Report.select().sort_by(desc(Report.date)).first()

    current_report = Report(date=datetime.now())
    db.commit()
    if last_report is not None:
        current_report.config(last_report.date)
    else:
        current_report.config()

    print_summary_report(current_report, last_report)
    email_body = compile_email_body(current_report, last_report)
    print(email_body)
    subject = f"SourceClear -- Scan Date {get_date()}"
    create_email_with_thunderbird(mailing_list, subject, email_body)


def print_summary_report(current_report, last_report):
    print()
    try:
        if last_report is not None:
            print(f"Number of projects: {current_report.projects.count()}")
            print(f"Change in high: {current_report.severity_high-last_report.severity_high}")
            print(f"Change in medium: {current_report.severity_medium-last_report.severity_medium}")
            print(f"Change in low: {current_report.severity_low-last_report.severity_low}")
        else:
            print("No previous report to compare with")

        print(f"""
Summary

Vulnerability Severity: High: {current_report.severity_high} ( {current_report.level_diff(last_report, Severity.high)} )
Vulnerability Severity: Medium: {current_report.severity_medium} ( {current_report.level_diff(last_report, Severity.medium)} )
Vulnerability Severity: Low: {current_report.severity_low} ( {current_report.level_diff(last_report, Severity.low)} )
        """, flush=True)

        change = current_report.projects_with_change(last_report)
        print("Projects with increased vulnerabilities", flush=True)
        if len(change['increase']) > 0:
            for increase in sorted(change['increase']):
                print(increase)
        else:
            print("None")

        print()
        print("Projects with decreased vulnerabilities", flush=True)
        if len(change['decrease']) > 0:
            for decrease in sorted(change['decrease']):
                print(decrease)
        else:
            print("None")

    except TypeError as err:
        print('lol')
        print(err)
    print()


def detailed_html(current_report, last_report):
    try:
        output = "<p>"
        change = current_report.projects_with_change(last_report)
        output += "<b>Projects with increased vulnerabilities</b><ul>"
        if len(change['increase']) > 0:
            for increase in sorted(change['increase']):
                output += f"<li>{increase}</li>"
        else:
            output += "<li>None</li>"
        output += "</ul></p><p>"
        output += "<b>Projects with decreased vulnerabilities</b><ul>"
        if len(change['decrease']) > 0:
            for decrease in sorted(change['decrease']):
                output += f"<li>{decrease}"
        else:
            output += "<li>None</li>"
        output += "</ul></p>"
    except TypeError:
        output = "Error on previous report to compare"
    return output


def compile_email_body(current_report, last_report):
    body = ""

    intro = "<p>Hi everyone.</p><p>Please find attached this weeks SourceClear scan report</p>"
    summary = f"<p><b>Summary</b><ul><li><font color='red'>Vulnerability Severity: High: </font> {current_report.severity_high} ( {current_report.level_diff(last_report, Severity.high)} )</li><li>Vulnerability Severity: Medium: {current_report.severity_medium} ( {current_report.level_diff(last_report, Severity.medium)} )</li><li>Vulnerability Severity: Low: {current_report.severity_low} ( {current_report.level_diff(last_report, Severity.low)} )</li></ul></p>"
    detailed = detailed_html(current_report, last_report)
    closing = "<p>*** Internal use only ***</p><p>Any work or tickets create from the information shared in this report should only be visible Internally</p><p>Scanning History can be found <a href='https://docs.google.com/document/d/1vne5AMVgYQIFcB4mqeX8magcEzQjRC_4rlH3VeH997I/edit#heading=h.n63e2poehf03'>HERE</a></br>Scanning History graph can be found <a href='https://docs.google.com/spreadsheets/d/13WjJlNIqjA9uESB_C9Qt3BHgEqLtfGOui88Jp2t-so0/edit#gid=0'>HERE</a></p>"
    body += intro
    body += summary
    body += detailed
    body += closing
    return body
