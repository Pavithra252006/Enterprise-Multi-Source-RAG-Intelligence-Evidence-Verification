#!/usr/bin/env python3
"""
generate_corpus.py
==================
Generates the full synthetic "Acme Corp" corpus under backend/data/raw/.

Files produced
--------------
1.  policy_handbook_v1_2022.pdf   – Remote work: 2 days/wk, expense limit $150/day
2.  policy_handbook_v2_2024.pdf   – Remote work: 3 days/wk, expense limit $200/day  ← CONTRADICTION #1 & #2
3.  q3_sales_headcount.xlsx       – Q3 Revenue $4.2 M, headcount 312
4.  it_security_policy.html       – IT password & device policy
5.  vendor_contracts.csv          – Vendor list with contract values
6.  executive_compensation.pdf    – RESTRICTED (access_level 4)
7.  annual_report_2021.pdf        – Outdated; states headcount 290, revenue $3.1 M ← CONTRADICTION #3 (headcount vs xlsx)
8.  annual_report_2024.pdf        – Current; supersedes 2021 report
9.  manifest.json

Planted contradictions (summary)
---------------------------------
C1: Remote-work days       – v1=2 days/wk vs v2=3 days/wk
C2: Daily expense limit    – v1=$150/day  vs v2=$200/day
C3: Q3 headcount           – 2021 report=290  vs q3_sales_headcount.xlsx=312
C4: Q3 Revenue             – 2021 report=$3.1M vs q3_sales_headcount.xlsx=$4.2M  (different year, same label)
"""

import json
import os
import csv
from pathlib import Path

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False
    print("WARNING: reportlab not installed – PDFs will be generated as plain text stubs.")

try:
    import openpyxl
    OPENPYXL_OK = True
except ImportError:
    OPENPYXL_OK = False
    print("WARNING: openpyxl not installed – XLSX will be generated as CSV stub.")

RAW_DIR = Path(__file__).parent / "backend" / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: PDF builder
# ─────────────────────────────────────────────────────────────────────────────
def make_pdf(path: Path, title: str, sections: list[tuple[str, str]]) -> None:
    """Create a simple PDF with section headings and body text."""
    if not REPORTLAB_OK:
        # Fallback: write a .txt file with same name
        txt_path = path.with_suffix(".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"=== {title} ===\n\n")
            for heading, body in sections:
                f.write(f"--- {heading} ---\n{body}\n\n")
        print(f"  [stub txt] {txt_path.name}")
        return

    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    body.leading = 14

    story = [Paragraph(title, h1), Spacer(1, 0.3 * inch)]
    for heading, text in sections:
        story.append(Paragraph(heading, h2))
        story.append(Spacer(1, 0.1 * inch))
        for para in text.split("\n\n"):
            story.append(Paragraph(para.strip(), body))
            story.append(Spacer(1, 0.1 * inch))
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    print(f"  [pdf] {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Policy Handbook v1 (2022)
# ─────────────────────────────────────────────────────────────────────────────
def gen_policy_v1():
    make_pdf(
        RAW_DIR / "policy_handbook_v1_2022.pdf",
        "Acme Corp Employee Policy Handbook – Version 1.0 (2022)",
        [
            ("1. Introduction",
             "This handbook sets forth the policies governing employment at Acme Corp as of January 1, 2022. "
             "All employees are expected to read, understand, and comply with these policies."),

            ("2. Remote Work Policy",
             "Acme Corp supports a hybrid work model. Employees are permitted to work remotely up to "
             "TWO (2) days per week, subject to manager approval. The remaining days must be spent "
             "at an approved Acme Corp office location.\n\n"
             "Remote work eligibility is subject to role requirements and performance standing. "
             "Employees must maintain secure VPN connectivity on all remote workdays."),

            ("3. Expense Reimbursement",
             "Employees may claim reimbursement for pre-approved business expenses. "
             "The maximum daily meal and incidental expense (M&IE) allowance is USD $150 per day "
             "for domestic travel and USD $200 per day for international travel.\n\n"
             "All expense claims must be submitted within 30 days of incurrence with original receipts. "
             "Submissions exceeding the per-diem limit will be rejected automatically."),

            ("4. Code of Conduct",
             "All Acme Corp employees must maintain the highest ethical standards. "
             "Conflicts of interest must be disclosed in writing to HR within 5 business days of arising. "
             "Violations may result in disciplinary action up to and including termination."),

            ("5. Leave Entitlements",
             "Full-time employees accrue 15 days of paid annual leave per calendar year. "
             "Unused leave may be carried over up to a maximum of 10 days. "
             "Sick leave is granted at 10 days per annum and is non-transferable."),

            ("6. Performance Reviews",
             "Performance reviews are conducted semi-annually in June and December. "
             "Employees rated 'Exceeds Expectations' for two consecutive cycles are eligible for "
             "accelerated promotion consideration. Merit-based salary adjustments are applied in January."),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Policy Handbook v2 (2024) – CONTRADICTIONS planted
# ─────────────────────────────────────────────────────────────────────────────
def gen_policy_v2():
    make_pdf(
        RAW_DIR / "policy_handbook_v2_2024.pdf",
        "Acme Corp Employee Policy Handbook – Version 2.0 (2024)",
        [
            ("1. Introduction",
             "This handbook supersedes all prior versions and sets forth updated policies "
             "governing employment at Acme Corp as of March 1, 2024. "
             "Employees must review the changes highlighted throughout this document."),

            ("2. Remote Work Policy",
             # ⚠️ CONTRADICTION #1: v1 says 2 days, v2 says 3 days
             "Following an internal workforce survey and benchmarking against industry peers, "
             "Acme Corp has expanded the hybrid work entitlement. Employees are now permitted to "
             "work remotely up to THREE (3) days per week, effective March 1, 2024. "
             "Manager approval is still required for schedules exceeding three remote days.\n\n"
             "Employees must maintain a dedicated workspace and comply with the updated IT Security "
             "Policy (see it_security_policy) when working remotely."),

            ("3. Expense Reimbursement",
             # ⚠️ CONTRADICTION #2: v1 says $150/day domestic, v2 says $200/day domestic
             "The daily M&IE reimbursement cap has been revised to reflect current cost-of-living "
             "indices. Effective January 1, 2024, the domestic per-diem allowance is USD $200 per day "
             "and the international allowance is USD $280 per day.\n\n"
             "A new automated expense portal (ExpenseIQ) is now mandatory for all submissions. "
             "Paper receipts must be digitised and uploaded within 14 days of incurrence."),

            ("4. Code of Conduct",
             "The code of conduct has been expanded to include guidance on AI tool usage. "
             "Employees must not input proprietary or customer data into external AI services "
             "without prior written approval from the Chief Information Security Officer.\n\n"
             "All other conduct provisions from Version 1.0 remain unchanged."),

            ("5. Leave Entitlements",
             "Annual leave entitlement increases to 18 days for employees with 3 or more years of service. "
             "All other leave provisions remain unchanged from Version 1.0."),

            ("6. Performance Reviews",
             "The cadence of performance reviews has changed to an annual cycle in December, "
             "replacing the prior semi-annual schedule. Mid-year check-ins are still encouraged "
             "but are informal and not recorded in the HR system."),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Q3 Sales & Headcount XLSX
# ─────────────────────────────────────────────────────────────────────────────
def gen_q3_xlsx():
    path = RAW_DIR / "q3_sales_headcount.xlsx"
    if not OPENPYXL_OK:
        # fallback CSV
        with open(path.with_suffix(".csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows([
                ["Metric", "Q1", "Q2", "Q3", "Q4 (Forecast)"],
                ["Revenue (USD M)", 3.6, 3.9, 4.2, 4.5],
                ["Gross Margin (%)", 61, 63, 65, 66],
                ["New Customers", 45, 52, 61, 70],
                ["Churn Rate (%)", 2.1, 1.9, 1.7, 1.5],
                [],
                ["Headcount", "Engineering", "Sales", "Operations", "Total"],
                # ⚠️ CONTRADICTION #3: Total=312 here vs 290 in 2021 annual report (different year labels cause confusion)
                ["End of Q3 2024", 128, 94, 90, 312],
                ["End of Q2 2024", 121, 89, 87, 297],
                ["End of Q1 2024", 115, 82, 83, 280],
            ])
        print(f"  [csv stub] {path.with_suffix('.csv').name}")
        return

    wb = openpyxl.Workbook()

    # Sheet 1: Revenue
    ws1 = wb.active
    ws1.title = "Revenue"
    headers = ["Metric", "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024 (Forecast)"]
    ws1.append(headers)
    # ⚠️ Q3 Revenue = $4.2M – conflicts with 2021 report that used same "Q3" label with $3.1M
    revenue_data = [
        ["Revenue (USD M)", 3.6, 3.9, 4.2, 4.5],
        ["Gross Margin (%)", 61.0, 63.2, 65.1, 66.0],
        ["Operating Expenses (USD M)", 1.8, 1.9, 2.0, 2.1],
        ["EBITDA (USD M)", 0.4, 0.6, 0.7, 0.9],
        ["New Customers", 45, 52, 61, 70],
        ["Churn Rate (%)", 2.1, 1.9, 1.7, 1.5],
        ["Customer Satisfaction (NPS)", 42, 45, 49, 52],
    ]
    for row in revenue_data:
        ws1.append(row)

    # Sheet 2: Headcount
    ws2 = wb.create_sheet("Headcount")
    ws2.append(["Department", "Q1 2024", "Q2 2024", "Q3 2024"])
    # ⚠️ CONTRADICTION #3: Total headcount 312 vs 2021 report's 290 (same "annual" label)
    headcount_data = [
        ["Engineering", 115, 121, 128],
        ["Sales & Marketing", 82, 89, 94],
        ["Operations", 83, 87, 90],
        ["Total", 280, 297, 312],
    ]
    for row in headcount_data:
        ws2.append(row)
    ws2.append([])
    ws2.append(["Note: Q3 2024 headcount (312) includes 8 new hires starting September 1."])

    # Sheet 3: Regional breakdown
    ws3 = wb.create_sheet("Regional")
    ws3.append(["Region", "Q3 Revenue (USD M)", "Q3 Headcount", "Win Rate (%)"])
    regional = [
        ["North America", 2.1, 158, 34],
        ["EMEA", 1.4, 98, 29],
        ["APAC", 0.7, 56, 22],
    ]
    for row in regional:
        ws3.append(row)

    wb.save(str(path))
    print(f"  [xlsx] {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. IT Security Policy HTML
# ─────────────────────────────────────────────────────────────────────────────
def gen_it_security_html():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Acme Corp – IT Security Policy</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 900px; margin: 2rem auto; line-height: 1.7; color: #222; }
    h1 { color: #003087; border-bottom: 2px solid #003087; padding-bottom: 0.5rem; }
    h2 { color: #005EB8; margin-top: 2rem; }
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
    th, td { border: 1px solid #aaa; padding: 8px 12px; text-align: left; }
    th { background: #003087; color: white; }
    .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 0.75rem 1rem; }
    footer { margin-top: 3rem; font-size: 0.85rem; color: #666; }
  </style>
</head>
<body>
  <h1>Acme Corp IT Security Policy</h1>
  <p><strong>Document ID:</strong> IT-SEC-001 &nbsp;|&nbsp;
     <strong>Version:</strong> 3.2 &nbsp;|&nbsp;
     <strong>Effective:</strong> 2024-01-15 &nbsp;|&nbsp;
     <strong>Owner:</strong> Chief Information Security Officer</p>

  <h2>1. Purpose and Scope</h2>
  <p>This policy establishes mandatory security controls for all Acme Corp employees, contractors,
  and third-party vendors who access Acme Corp information systems. Compliance is mandatory and
  non-compliance may result in disciplinary action up to and including termination of employment or contract.</p>

  <h2>2. Password Requirements</h2>
  <table>
    <tr><th>Parameter</th><th>Requirement</th></tr>
    <tr><td>Minimum length</td><td>14 characters</td></tr>
    <tr><td>Complexity</td><td>Must include uppercase, lowercase, digit, and symbol</td></tr>
    <tr><td>Maximum age</td><td>90 days</td></tr>
    <tr><td>History</td><td>Last 12 passwords cannot be reused</td></tr>
    <tr><td>Multi-Factor Authentication</td><td>Mandatory for all accounts</td></tr>
  </table>

  <h2>3. Device Security</h2>
  <p>All endpoints (laptops, mobile devices) that access Acme Corp resources must:</p>
  <ul>
    <li>Have approved endpoint detection and response (EDR) software installed and active</li>
    <li>Maintain OS and application patches within 7 days of release for critical vulnerabilities</li>
    <li>Use full-disk encryption (BitLocker for Windows, FileVault for macOS)</li>
    <li>Be enrolled in Acme Corp Mobile Device Management (MDM) system</li>
    <li>Automatically lock after 5 minutes of inactivity</li>
  </ul>

  <h2>4. Remote Access</h2>
  <p>All remote access to Acme Corp internal networks must use the company-approved VPN client.
  Split tunnelling is prohibited. Employees working from public networks (cafes, airports) must
  use the VPN at all times.</p>

  <div class="warning">
    <strong>⚠ Important:</strong> Connecting to Acme Corp systems from a personal device that
    has not been approved via the BYOD programme is strictly prohibited.
  </div>

  <h2>5. Data Classification and Handling</h2>
  <table>
    <tr><th>Level</th><th>Label</th><th>Examples</th><th>Encryption Required</th></tr>
    <tr><td>1</td><td>Public</td><td>Marketing materials, job postings</td><td>In transit only</td></tr>
    <tr><td>2</td><td>Internal</td><td>Internal memos, project plans</td><td>In transit and at rest</td></tr>
    <tr><td>3</td><td>Confidential</td><td>Customer data, contracts</td><td>Always + access control</td></tr>
    <tr><td>4</td><td>Restricted</td><td>Board materials, exec compensation</td><td>Always + strict need-to-know</td></tr>
  </table>

  <h2>6. Incident Reporting</h2>
  <p>All suspected security incidents (phishing, malware, data loss) must be reported to
  <strong>security@acmecorp.internal</strong> within <strong>1 hour</strong> of discovery.
  Employees must not attempt to remediate incidents independently.</p>

  <h2>7. Acceptable Use</h2>
  <p>Acme Corp systems may be used for legitimate business purposes only. Prohibited activities include
  cryptocurrency mining, personal cloud storage sync, and installation of unapproved software.
  All internet traffic is monitored and logged for security purposes.</p>

  <h2>8. AI Tool Usage</h2>
  <p>External AI services (including but not limited to ChatGPT, Claude, Gemini) may not be used
  to process Acme Corp Confidential or Restricted data without explicit written approval from the CISO.
  Violation of this policy constitutes a data breach and will be treated accordingly.</p>

  <footer>
    <p>© 2024 Acme Corp. All rights reserved. | IT Security Policy IT-SEC-001 v3.2 |
    Next review date: 2025-01-15</p>
  </footer>
</body>
</html>
"""
    path = RAW_DIR / "it_security_policy.html"
    path.write_text(html, encoding="utf-8")
    print(f"  [html] {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Vendor Contracts CSV
# ─────────────────────────────────────────────────────────────────────────────
def gen_vendor_csv():
    path = RAW_DIR / "vendor_contracts.csv"
    rows = [
        ["vendor_id", "vendor_name", "category", "contract_value_usd", "start_date", "end_date",
         "auto_renew", "primary_contact", "sla_uptime_pct", "status"],
        ["V001", "CloudNest Technologies", "Cloud Infrastructure", 480000, "2023-01-01", "2025-12-31",
         "Yes", "alice.wu@cloudnest.com", 99.9, "Active"],
        ["V002", "DataShield Security", "Cybersecurity", 175000, "2024-03-01", "2026-02-28",
         "No", "bob.martin@datashield.io", 99.5, "Active"],
        ["V003", "OfficePrime Supplies", "Facilities", 62000, "2024-01-01", "2024-12-31",
         "Yes", "orders@officeprime.com", "N/A", "Active"],
        ["V004", "SwiftLogix Courier", "Logistics", 38500, "2023-06-01", "2025-05-31",
         "Yes", "contracts@swiftlogix.com", "N/A", "Active"],
        ["V005", "TalentBridge Staffing", "HR / Staffing", 220000, "2024-01-15", "2025-01-14",
         "No", "enterprise@talentbridge.com", "N/A", "Active"],
        ["V006", "InsightBI Analytics", "Business Intelligence", 95000, "2023-09-01", "2025-08-31",
         "Yes", "sales@insightbi.co", 99.0, "Active"],
        ["V007", "LegalEagle LLP", "Legal Services", 310000, "2022-07-01", "2026-06-30",
         "No", "acme@legaleagle.com", "N/A", "Active"],
        ["V008", "PrintWorks Co.", "Print & Marketing", 28000, "2024-04-01", "2025-03-31",
         "Yes", "b2b@printworks.com", "N/A", "Active"],
        ["V009", "NetStream ISP", "Connectivity", 54000, "2023-03-15", "2026-03-14",
         "Yes", "enterprise@netstream.net", 99.8, "Active"],
        ["V010", "AuditPro Partners", "Audit & Compliance", 140000, "2024-02-01", "2025-01-31",
         "No", "acme@auditpro.com", "N/A", "Active"],
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"  [csv] {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Executive Compensation (RESTRICTED – access_level 4)
# ─────────────────────────────────────────────────────────────────────────────
def gen_exec_comp():
    make_pdf(
        RAW_DIR / "executive_compensation.pdf",
        "RESTRICTED – Acme Corp Executive Compensation Report 2024",
        [
            ("CONFIDENTIAL – FOR BOARD USE ONLY",
             "This document contains sensitive compensation data. Distribution is limited to Board members "
             "and the Chief Human Resources Officer. Unauthorised disclosure is a serious policy violation "
             "and may constitute a breach of securities regulations."),

            ("CEO Compensation Package",
             "Base Salary: USD $850,000 per annum\n\n"
             "Annual Performance Bonus: Up to 150% of base salary ($1,275,000 maximum)\n\n"
             "Long-Term Incentive Plan (LTIP): 120,000 RSUs vesting over 4 years (25% per year)\n\n"
             "Other Benefits: Executive health plan, $15,000 annual car allowance, "
             "$20,000 annual financial planning allowance"),

            ("CFO Compensation Package",
             "Base Salary: USD $620,000 per annum\n\n"
             "Annual Performance Bonus: Up to 100% of base salary ($620,000 maximum)\n\n"
             "Long-Term Incentive Plan (LTIP): 75,000 RSUs vesting over 4 years\n\n"
             "Other Benefits: Executive health plan, $12,000 annual car allowance"),

            ("CTO Compensation Package",
             "Base Salary: USD $680,000 per annum\n\n"
             "Annual Performance Bonus: Up to 120% of base salary ($816,000 maximum)\n\n"
             "Long-Term Incentive Plan (LTIP): 90,000 RSUs vesting over 4 years\n\n"
             "Retention Bonus: $200,000 payable upon completion of Project Synapse milestone"),

            ("Compensation Governance",
             "All executive compensation decisions are made by the Board Compensation Committee "
             "following an independent benchmarking study conducted by TowerHall Advisors. "
             "The next review is scheduled for Q1 2025."),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Annual Report 2021 (OUTDATED – superseded by 2024)
# ─────────────────────────────────────────────────────────────────────────────
def gen_annual_2021():
    make_pdf(
        RAW_DIR / "annual_report_2021.pdf",
        "Acme Corp Annual Report 2021 – SUPERSEDED",
        [
            ("NOTICE: This report has been superseded by the 2024 Annual Report",
             "This document is retained for historical reference only. For current figures, "
             "please refer to annual_report_2024.pdf."),

            ("Company Overview",
             "Acme Corp was founded in 2015 and has grown to become a leading provider of "
             "enterprise data management solutions. As of year-end 2021, the company operates "
             "in three geographic regions: North America, EMEA, and APAC."),

            ("Financial Highlights 2021",
             # ⚠️ CONTRADICTION #4: Revenue label "Q3" used loosely in 2021 vs 2024 XLSX
             "Annual Revenue: USD $3.1 million\n\n"
             "Gross Margin: 58%\n\n"
             "The company achieved 28% year-over-year revenue growth, driven primarily by "
             "expansion in the North American mid-market segment."),

            ("Workforce",
             # ⚠️ CONTRADICTION #3: headcount 290 here vs 312 in q3_sales_headcount.xlsx (2024 data)
             "Total Headcount as of December 31, 2021: 290 employees\n\n"
             "The workforce grew by 45 employees during 2021, with the majority of new hires "
             "in Engineering (22) and Sales (15).\n\n"
             "Note: This figure is frequently confused with 2024 headcount data (312) "
             "in cross-document queries."),

            ("Strategic Outlook 2022",
             "Management is targeting 25% revenue growth for 2022, supported by the launch "
             "of three new product modules and geographic expansion into Southeast Asia. "
             "Hiring is expected to accelerate in H1 2022 with a target of 50 additional FTEs."),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# 8. Annual Report 2024 (CURRENT)
# ─────────────────────────────────────────────────────────────────────────────
def gen_annual_2024():
    make_pdf(
        RAW_DIR / "annual_report_2024.pdf",
        "Acme Corp Annual Report 2024",
        [
            ("Executive Summary",
             "2024 marks Acme Corp's strongest year on record. The company achieved significant "
             "growth across all key metrics, driven by product innovation and strategic market expansion. "
             "This report supersedes all prior annual reports."),

            ("Financial Performance",
             "Full-Year 2024 Revenue: USD $16.2 million (37% YoY growth)\n\n"
             "Q3 2024 Revenue: USD $4.2 million – consistent with the Q3 Sales & Headcount Report\n\n"
             "Gross Margin: 65.1% (up from 58% in 2021)\n\n"
             "EBITDA: USD $2.8 million (positive for the second consecutive year)"),

            ("Workforce and Culture",
             "Total Headcount as of September 30, 2024: 312 employees\n\n"
             "Full-year hiring target: 340 employees by December 31, 2024\n\n"
             "Employee NPS: 72 (top quartile for our industry peer group)\n\n"
             "Attrition rate: 8.2% (industry average: 12.4%)"),

            ("Product Portfolio",
             "Acme Corp now offers five enterprise modules: DataVault, InsightIQ, SecureSync, "
             "ComplianceBot, and the newly launched NeuralMesh AI platform. "
             "NeuralMesh contributed USD $1.1 million in Q3 2024 revenue, exceeding initial projections."),

            ("Outlook 2025",
             "Management is targeting USD $22 million in full-year 2025 revenue, representing "
             "36% growth. Key investments will be in AI product development, APAC market expansion, "
             "and a new Singapore engineering hub (targeted headcount: 40 by Q2 2025)."),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# 9. manifest.json
# ─────────────────────────────────────────────────────────────────────────────
def gen_manifest():
    manifest = [
        {
            "filename": "policy_handbook_v1_2022.pdf",
            "title": "Acme Corp Employee Policy Handbook v1.0 (2022)",
            "source_type": "pdf",
            "version": "1.0",
            "doc_date": "2022-01-01",
            "access_level": 2,
            "allowed_roles": ["analyst", "manager", "executive"],
            "superseded_by": "policy_handbook_v2_2024.pdf",
            "notes": "Contradicts v2 on remote-work days (2 vs 3) and expense limit ($150 vs $200)"
        },
        {
            "filename": "policy_handbook_v2_2024.pdf",
            "title": "Acme Corp Employee Policy Handbook v2.0 (2024)",
            "source_type": "pdf",
            "version": "2.0",
            "doc_date": "2024-03-01",
            "access_level": 2,
            "allowed_roles": ["analyst", "manager", "executive"],
            "notes": "Current authoritative policy"
        },
        {
            "filename": "q3_sales_headcount.xlsx",
            "title": "Q3 2024 Sales & Headcount Report",
            "source_type": "xlsx",
            "version": "1.0",
            "doc_date": "2024-10-01",
            "access_level": 2,
            "allowed_roles": ["analyst", "manager", "executive"],
            "notes": "Headcount 312 conflicts with 2021 annual report figure 290"
        },
        {
            "filename": "it_security_policy.html",
            "title": "Acme Corp IT Security Policy v3.2",
            "source_type": "html",
            "version": "3.2",
            "doc_date": "2024-01-15",
            "access_level": 1,
            "allowed_roles": None,
            "notes": "Public – all employees"
        },
        {
            "filename": "vendor_contracts.csv",
            "title": "Active Vendor Contracts Register",
            "source_type": "csv",
            "version": "1.0",
            "doc_date": "2024-10-01",
            "access_level": 3,
            "allowed_roles": ["manager", "executive"],
            "notes": "Confidential – managers and above"
        },
        {
            "filename": "executive_compensation.pdf",
            "title": "Acme Corp Executive Compensation Report 2024",
            "source_type": "pdf",
            "version": "1.0",
            "doc_date": "2024-01-01",
            "access_level": 4,
            "allowed_roles": ["executive"],
            "notes": "RESTRICTED – board/executive only"
        },
        {
            "filename": "annual_report_2021.pdf",
            "title": "Acme Corp Annual Report 2021 (Outdated)",
            "source_type": "pdf",
            "version": "2021",
            "doc_date": "2022-03-15",
            "access_level": 2,
            "allowed_roles": ["analyst", "manager", "executive"],
            "superseded_by": "annual_report_2024.pdf",
            "notes": "OUTDATED – superseded by 2024 report. Headcount 290 conflicts with 2024 data 312"
        },
        {
            "filename": "annual_report_2024.pdf",
            "title": "Acme Corp Annual Report 2024",
            "source_type": "pdf",
            "version": "2024",
            "doc_date": "2024-12-01",
            "access_level": 2,
            "allowed_roles": ["analyst", "manager", "executive"],
            "notes": "Current – supersedes all prior annual reports"
        },
    ]
    path = RAW_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [json] {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nGenerating Acme Corp synthetic corpus -> {RAW_DIR}\n")
    gen_policy_v1()
    gen_policy_v2()
    gen_q3_xlsx()
    gen_it_security_html()
    gen_vendor_csv()
    gen_exec_comp()
    gen_annual_2021()
    gen_annual_2024()
    gen_manifest()
    print(f"\nCorpus generation complete. Files in: {RAW_DIR}\n")
