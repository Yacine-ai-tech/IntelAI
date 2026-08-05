#!/usr/bin/env python3
"""
NexaCore Technologies — PDF Report Generator
============================================
Generates realistic PDF documents from the markdown source files.
Uses fpdf2 for PDF generation.

Usage:
  python3 scripts/generate_pdfs.py
"""

from __future__ import annotations
import os
import re
import sys
from pathlib import Path
from fpdf import FPDF

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class NexaCorePDF(FPDF):
    """Branded PDF with NexaCore header/footer."""

    def __init__(self, title: str, category: str):
        super().__init__()
        self.doc_title = title
        self.doc_category = category
        self.set_auto_page_break(auto=True, margin=20)
        self.add_page()
        self._add_header()

    @staticmethod
    def _ascii(text: str) -> str:
        """Replace non-latin-1 chars for fpdf2 core font compatibility."""
        replacements = {
            '\u2014': '--',    # em dash
            '\u2013': '-',     # en dash
            '\u2019': "'",     # right single quote
            '\u2018': "'",     # left single quote
            '\u201c': '"',     # left double quote
            '\u201d': '"',     # right double quote
            '\u2192': '->',    # right arrow
            '\u2190': '<-',    # left arrow
            '\u2026': '...',   # ellipsis
            '\u00b0': ' deg',  # degree
            '\u00a9': '(c)',   # copyright
            '\u00ae': '(R)',   # registered
            '\u00e9': 'e',     # e acute
            '\u00e8': 'e',     # e grave
            '\u00ea': 'e',     # e circumflex
            '\u00e0': 'a',     # a grave
            '\u00e2': 'a',     # a circumflex
            '\u00fc': 'u',     # u umlaut
            '\u00f6': 'o',     # o umlaut
            '\u00e4': 'a',     # a umlaut
            '\u00df': 'ss',    # sharp s
            '\u2022': '-',     # bullet
            '\u2715': 'x',     # multiply sign
            '\u2713': 'v',     # check mark
            '\u00d7': 'x',     # multiplication sign
            '\u00f7': '/',     # division sign
            '\u00b1': '+/-',   # plus-minus
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
        # Strip any remaining non-latin-1 characters
        return text.encode('latin-1', errors='replace').decode('latin-1')

    def _add_header(self):
        # Header bar
        self.set_fill_color(15, 23, 42)  # dark navy
        self.rect(0, 0, 210, 18, style="F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.set_xy(10, 5)
        self.cell(0, 8, "NexaCore Technologies - CONFIDENTIAL", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(10)

    def header(self):
        pass  # Handled in __init__ for first page only

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"NexaCore Technologies -- {self.doc_category} | Page {self.page_no()}", align="C")

    def add_title(self, title: str):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(15, 23, 42)
        self.multi_cell(0, 10, self._ascii(title))
        self.ln(3)

    def add_subtitle(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(90, 90, 90)
        self.multi_cell(0, 5, self._ascii(text))
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def add_section_heading(self, text: str, level: int = 1):
        self.ln(4)
        if level == 1:
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(15, 23, 42)
        elif level == 2:
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(30, 64, 175)
        else:
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, self._ascii(text))
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def add_body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, self._ascii(text))
        self.ln(2)

    def add_table_row(self, cells: list[str], header: bool = False, col_widths: list[float] | None = None):
        if col_widths is None:
            col_widths = [190 / len(cells)] * len(cells)
        if header:
            self.set_fill_color(30, 64, 175)
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 9)
        else:
            self.set_fill_color(248, 250, 252)
            self.set_text_color(30, 30, 30)
            self.set_font("Helvetica", "", 9)
        x_start = self.get_x()
        y_start = self.get_y()
        for i, (cell, width) in enumerate(zip(cells, col_widths)):
            fill = header or (i == 0)
            self.set_x(x_start + sum(col_widths[:i]))
            self.set_y(y_start)
            self.cell(width, 7, self._ascii(str(cell))[:45], border=1, fill=(i == 0 or header))
        self.ln(7)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)

    def add_info_badge(self, label: str, value: str, color: tuple = (30, 64, 175)):
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        self.cell(50, 8, self._ascii(f" {label}: {value}"), border=0, fill=True, ln=0)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        self.ln(10)


def generate_board_report_pdf(dry_run: bool = False) -> None:
    """Generate Q3 2025 Board Recovery Report PDF."""
    output_path = DATA_DIR / "BoardReports" / "NexaCore_Q3_2025_Board_Recovery_Report.pdf"
    if dry_run:
        print(f"  [DRY-RUN] Would write: {output_path.relative_to(DATA_DIR)}")
        return

    pdf = NexaCorePDF("Q3 2025 Board Recovery Report", "Board Reports")
    pdf.add_title("NexaCore Technologies")
    pdf.add_subtitle("Q3 2025 Operational Recovery Report | July 1 – September 30, 2025\nPrepared by: Office of the CEO | Distribution: Board of Directors — Confidential")

    pdf.add_section_heading("Executive Summary")
    pdf.add_body(
        "Q3 2025 marks the beginning of NexaCore's recovery from the compound crises of 2024 "
        "(high customer churn, talent attrition, cybersecurity breach) and Q1-Q2 2025 "
        "(operational meltdown and logistics disruption). While full recovery is not yet complete, "
        "leading indicators are trending positively across all seven domains.\n\n"
        "ARR: $94.2M (Q3 2025) | Monthly Churn: 2.1% | Uptime: 99.4% | OEE: 74.2% | Logistics OTD: 88.4%"
    )

    pdf.add_section_heading("Domain Performance Summary", level=2)
    headers = ["Domain", "Key Metric", "Q3 2025", "Target", "Status"]
    widths = [35, 45, 30, 30, 30]
    pdf.add_table_row(headers, header=True, col_widths=widths)
    rows = [
        ["Finance", "ARR ($M)", "$94.2", "$96.0", "Near target"],
        ["Growth", "Monthly Churn", "2.1%", "<=1.5%", "Recovering"],
        ["Growth", "NRR", "102%", "108%", "Below target"],
        ["People", "Turnover TTM", "14.2%", "<=13%", "Near target"],
        ["IT Security", "Uptime", "99.4%", ">=99.5%", "Near target"],
        ["IT Security", "Critical CVEs", "2 open", "<=3", "On target"],
        ["Operations", "OEE", "74.2%", ">=75%", "Near target"],
        ["Logistics", "OTD", "88.4%", ">=92%", "Below target"],
        ["ESG", "Scope 1+2 tCO2e", "294", "<=280", "Below target"],
    ]
    for row in rows:
        pdf.add_table_row(row, col_widths=widths)

    pdf.ln(5)
    pdf.add_section_heading("Financial Highlights", level=2)
    pdf.add_body(
        "Series B ($15M) closed April 2024 extended cash runway to 18+ months. "
        "Current monthly burn rate: $840K. ARR recovery from $88.1M trough (Q1 2025) to $94.2M (+6.9%). "
        "Gross margin compression (68.8% vs. 70% target) driven by elevated hardware COGS post-Flex supply disruption. "
        "EBITDA expected to reach break-even in Q1 2026 as churn normalizes and headcount costs plateau."
    )

    pdf.add_section_heading("Customer Retention Recovery", level=2)
    pdf.add_body(
        "The retention crisis (peak churn 5.4% Feb 2024) has been substantially addressed:\n"
        "- 5 CSMs redeployed to retention taskforce (Q1 2024) — now permanent team structure\n"
        "- API v2 white-glove migration completed for all 22 at-risk accounts (April 2024)\n"
        "- Support SLA restored to <2h P1 response (3 support engineers hired Q1 2024)\n"
        "- Slack/Teams integration launching October 15 (addresses top churn driver)\n"
        "- LTV:CAC recovering: 1.1x (Feb 2024) → 2.2x (Q3 2025) — target 3.0x by Q2 2026"
    )

    pdf.add_section_heading("Security Posture Post-Breach", level=2)
    pdf.add_body(
        "The October 2024 cybersecurity incident (unauthorized access via compromised JWT key) has driven "
        "significant improvements to NexaCore's security architecture:\n"
        "- HashiCorp Vault deployment: 94% of secrets migrated (completion: Q4 2025)\n"
        "- Zero-trust network architecture (Istio service mesh): 60% implemented\n"
        "- External penetration testing (NCC Group) completed Q1 2025 — 3 critical findings, all remediated\n"
        "- SOC 2 Type II recertification: passed March 2025 audit\n"
        "- Security compliance score: 74.2% → 91.8% (Oct 2024 to Sep 2025)"
    )

    pdf.add_section_heading("Q4 2025 Priorities", level=2)
    pdf.add_table_row(["Priority", "Owner", "Target Date"], header=True, col_widths=[80, 50, 60])
    q4_priorities = [
        ["Slack/Teams integration GA release", "CPO / Engineering", "Oct 15, 2025"],
        ["HashiCorp Vault 100% adoption", "DevOps / Security", "Nov 30, 2025"],
        ["ARR target: $100M run-rate", "CEO / Sales", "Dec 31, 2025"],
        ["OEE target: >=75%", "Operations", "Dec 31, 2025"],
        ["Logistics OTD: >=92%", "Logistics", "Dec 31, 2025"],
    ]
    for row in q4_priorities:
        pdf.add_table_row(row, col_widths=[80, 50, 60])

    pdf.ln(5)
    pdf.add_body("Full recovery to pre-crisis baseline metrics projected Q2 2026. FY2026 ARR forecast: $108-$112M.")
    pdf.add_body("\n\nPrepared by: Office of the CEO | Confidential — Board Distribution Only")

    pdf.output(str(output_path))
    print(f"  ✓ BoardReports/NexaCore_Q3_2025_Board_Recovery_Report.pdf")


def generate_security_incident_report_pdf(dry_run: bool = False) -> None:
    """Generate Cybersecurity Breach Incident Report PDF."""
    output_path = DATA_DIR / "BoardReports" / "NexaCore_CyberBreach_Incident_Report_Oct2024.pdf"
    if dry_run:
        print(f"  [DRY-RUN] Would write: {output_path.relative_to(DATA_DIR)}")
        return

    pdf = NexaCorePDF("Cybersecurity Breach — Incident Report", "Security")
    pdf.add_title("Cybersecurity Breach — Post-Incident Report")
    pdf.add_subtitle(
        "October 2024 Security Incident | Classification: CONFIDENTIAL\n"
        "Prepared by: Rafael Gomes (CTO) + Sofia Chen (VP Engineering)\n"
        "Distribution: Board of Directors + Legal + DPO"
    )

    pdf.add_section_heading("Incident Summary")
    pdf.add_body(
        "On September 28, 2024 at 03:47 UTC, NexaCore's automated monitoring system detected "
        "anomalous outbound traffic from the authentication microservice. Investigation confirmed "
        "unauthorized API access via a compromised JWT signing key stored in plaintext in AWS SSM "
        "Parameter Store. The attacker accessed read-only audit log data for 340 enterprise accounts.\n\n"
        "Full service was restored October 2, 2024 at 14:00 UTC — 78 hours after detection.\n\n"
        "PLATFORM AVAILABILITY: 91.2% over the 7-day incident window (SLA: 99.5%)\n"
        "DATA EXFILTRATION: No evidence found. Audit logs accessed (account IDs + timestamps only)."
    )

    pdf.add_section_heading("Timeline of Events", level=2)
    pdf.add_table_row(["Date/Time (UTC)", "Event"], header=True, col_widths=[55, 135])
    timeline = [
        ["Sep 28, 03:47", "Automated alert: anomalous outbound traffic from auth microservice"],
        ["Sep 28, 04:22", "SOC on-call confirmed unauthorized API access. P0 declared."],
        ["Sep 28, 06:00", "JWT signing key rotated. 2,400 active sessions force-expired."],
        ["Sep 28, 08:00", "All Enterprise customers notified via email + phone."],
        ["Sep 29-Oct 1", "Digital forensics: attacker accessed read-only audit logs (340 accounts)"],
        ["Oct 1, 14:00", "GDPR Article 33 notification filed to Dutch DPA (within 72h window)."],
        ["Oct 2, 14:00", "Full service restoration. Post-mortem initiated."],
        ["Oct 4", "IMDSv2 enforced across all EC2 instances fleet-wide."],
        ["Oct 5", "All SSM Parameter Store secrets migrated to SecureString encryption."],
        ["Nov 1", "HashiCorp Vault enterprise contract signed. Implementation started."],
    ]
    for row in timeline:
        pdf.add_table_row(row, col_widths=[55, 135])

    pdf.ln(5)
    pdf.add_section_heading("Root Cause Analysis", level=2)
    pdf.add_body(
        "TECHNICAL ROOT CAUSE: JWT signing key stored as plaintext in AWS SSM Parameter Store "
        "(should have been SecureString). Attacker accessed it via a compromised EC2 instance metadata "
        "service (IMDSv1 vulnerability).\n\n"
        "CONTRIBUTING PROCESS FAILURES:\n"
        "1. Secret rotation policy did not cover infrastructure keys (only API keys)\n"
        "2. IMDSv2 enforcement was optional, not mandatory, fleet-wide\n"
        "3. Outbound traffic anomaly detection threshold set 10x too high\n"
        "4. Incident response runbook for auth service compromise was 18 months out of date\n"
        "5. No separation of duties between secret creation and access (single IAM role)"
    )

    pdf.add_section_heading("Financial Impact", level=2)
    pdf.add_table_row(["Cost Category", "Amount (USD)"], header=True, col_widths=[120, 70])
    costs = [
        ["SLA credits to Enterprise customers (10% × affected months)", "$84,200"],
        ["Engineering overtime (incident response, 78 hours × 8 engineers)", "$18,400"],
        ["External forensics (Mandiant, 5 days)", "$42,000"],
        ["HashiCorp Vault license + implementation", "$138,000"],
        ["External penetration testing (NCC Group, Q1 2025)", "$48,000"],
        ["Additional security engineer hire (annual)", "$240,000"],
        ["Lost ARR (churn triggered by breach, estimated)", "$380,000"],
        ["TOTAL DIRECT + INDIRECT COST", "~$950,600"],
    ]
    for row in costs:
        pdf.add_table_row(row, col_widths=[120, 70])

    pdf.ln(5)
    pdf.add_section_heading("Remediation Status", level=2)
    pdf.add_table_row(["Action Item", "Status", "Completed"], header=True, col_widths=[100, 45, 45])
    actions = [
        ["JWT key rotation (all environments)", "DONE", "Oct 2, 2024"],
        ["IMDSv2 fleet-wide enforcement", "DONE", "Oct 4, 2024"],
        ["SSM Parameter Store encryption audit", "DONE", "Oct 5, 2024"],
        ["Admin password reset + MFA enforcement", "DONE", "Oct 3, 2024"],
        ["HashiCorp Vault deployment (94%)", "IN PROGRESS", "Nov 2025 target"],
        ["Istio service mesh (60% complete)", "IN PROGRESS", "Q1 2026 target"],
        ["NCC Group penetration test", "DONE", "Mar 2025"],
        ["SOC 2 Type II recertification", "DONE", "Mar 2025"],
    ]
    for row in actions:
        pdf.add_table_row(row, col_widths=[100, 45, 45])

    pdf.output(str(output_path))
    print(f"  ✓ BoardReports/NexaCore_CyberBreach_Incident_Report_Oct2024.pdf")


def generate_supplier_rfp_pdf(dry_run: bool = False) -> None:
    """Generate a supplier RFP document PDF."""
    output_path = DATA_DIR / "Procurement" / "NexaCore_RFP_LogisticsProvider_2025.pdf"
    if dry_run:
        print(f"  [DRY-RUN] Would write: {output_path.relative_to(DATA_DIR)}")
        return

    pdf = NexaCorePDF("Logistics Provider RFP 2025", "Procurement")
    pdf.add_title("Request for Proposal: Global Freight & Logistics Services")
    pdf.add_subtitle(
        "RFP Reference: RFP-LOG-2025-001\n"
        "Issue Date: January 15, 2025 | Response Deadline: February 28, 2025\n"
        "Issued by: NexaCore Technologies Procurement Team"
    )

    pdf.add_section_heading("1. Company Overview")
    pdf.add_body(
        "NexaCore Technologies is a B2B SaaS + hardware company headquartered in Austin, Texas. "
        "We provide AI-powered analytics solutions bundled with IoT edge compute hardware (NXT-EC series). "
        "Annual shipment volume: approximately 2,400 domestic + 480 international consignments per year. "
        "We are issuing this RFP following service disruptions with our current provider and a disputed "
        "invoice regarding fuel surcharge application (Dispute Ref: DISP-FEDEX-2025-0847).\n\n"
        "Hardware category: IoT edge computing modules with embedded lithium batteries. "
        "Some units classified ECCN 5A992 — carrier must be EAR-experienced."
    )

    pdf.add_section_heading("2. Scope of Services Required")
    pdf.add_body(
        "2.1 US DOMESTIC\n"
        "- Priority express freight (next-day and 2-day) for ~180 consignments/month\n"
        "- Standard ground freight for ~20 consignments/month\n"
        "- Weight range: 0.5 kg to 45 kg per consignment\n\n"
        "2.2 INTERNATIONAL\n"
        "- EU destinations: France, Netherlands, Germany, Belgium, UK (~40 consignments/month)\n"
        "- Customs brokerage services included (EU VAT and IOSS compliance required)\n"
        "- Track and trace with real-time API access\n\n"
        "2.3 VALUE-ADDED SERVICES\n"
        "- Lithium battery (UN3481) compliant handling and IATA documentation\n"
        "- ECCN 5A992 export license coordination\n"
        "- Freight management portal with bulk label generation\n"
        "- EDI integration (X12 850/856 or equivalent)"
    )

    pdf.add_section_heading("3. Evaluation Criteria", level=2)
    pdf.add_table_row(["Criterion", "Weight"], header=True, col_widths=[140, 50])
    criteria = [
        ["Price competitiveness (vs. FedEx 2024 contracted rates)", "30%"],
        ["Service level reliability (OTD performance data required)", "25%"],
        ["Technology integration capability (API, EDI, portal)", "20%"],
        ["Hazardous goods (lithium battery) and export control experience", "15%"],
        ["Account management and escalation process", "10%"],
    ]
    for row in criteria:
        pdf.add_table_row(row, col_widths=[140, 50])

    pdf.ln(5)
    pdf.add_section_heading("4. Required Response Format", level=2)
    pdf.add_body(
        "Respondents must include:\n"
        "a) Company profile + customer references (minimum 3 tech hardware companies)\n"
        "b) Rate card for all US domestic and international lanes specified\n"
        "c) Fuel surcharge policy and contractual cap commitment\n"
        "d) OTD performance data (last 24 months, auditable)\n"
        "e) Hazmat and export control compliance certifications\n"
        "f) Sample MSA and freight terms\n\n"
        "Submit to: procurement@nexacore.ai | Subject: RFP-LOG-2025-001 Response\n"
        "Deadline: February 28, 2025, 17:00 CT"
    )

    pdf.output(str(output_path))
    print(f"  ✓ Procurement/NexaCore_RFP_LogisticsProvider_2025.pdf")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="NexaCore PDF Generator")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 55)
    print("NexaCore Technologies — PDF Report Generator")
    if args.dry_run:
        print("[DRY RUN MODE]")
    print("=" * 55)

    generate_board_report_pdf(args.dry_run)
    generate_security_incident_report_pdf(args.dry_run)
    generate_supplier_rfp_pdf(args.dry_run)

    print("\n✅ PDFs generated.")


if __name__ == "__main__":
    main()
