#!/usr/bin/env python3
"""
NexaCore Technologies — Comprehensive Enterprise Data Generator
================================================================
Generates realistic enterprise documents across all data types that
NexaCore Technologies would handle: PDF reports, invoices, contracts,
meeting notes, cloud infra data, HR records, support tickets, emails, etc.

All content is fictional but internally consistent with the 78-month
NexaCore scenario timeline (2020-01 to 2026-06).

Output structure:
  data/
    BoardReports/      - Quarterly/annual board reports (PDF + MD)
    Contracts/         - Supplier/SLA/customer contracts (MD/TXT)
    Invoices/          - Supplier invoices (JSON structured data)
    MeetingNotes/      - Board + team meeting minutes (MD)
    CloudInfra/        - AWS cost reports, infra configs (JSON)
    HR/                - Onboarding docs, performance reviews (MD)
    Legal/             - NDAs, compliance filings (MD)
    Procurement/       - Purchase orders, RFPs (MD/JSON)
    Support/           - Support ticket logs (JSON)
    Emails/            - Key executive emails (MD/TXT)

Usage:
  python3 scripts/generate_enterprise_data.py
  python3 scripts/generate_enterprise_data.py --type invoices
  python3 scripts/generate_enterprise_data.py --dry-run
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Any

# ── Output root ───────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ── Helpers ───────────────────────────────────────────────────────────────────

def write_file(path: Path, content: str, dry_run: bool = False) -> None:
    if dry_run:
        print(f"  [DRY-RUN] Would write: {path.relative_to(DATA_DIR.parent.parent)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✓ {path.relative_to(DATA_DIR)}")


def write_json(path: Path, data: Any, dry_run: bool = False) -> None:
    write_file(path, json.dumps(data, indent=2, default=str), dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CLOUD INFRASTRUCTURE DATA
# ═══════════════════════════════════════════════════════════════════════════════

def generate_cloud_infra(dry_run: bool) -> None:
    print("\n[CloudInfra] Generating AWS cost reports and infrastructure configs...")

    # Monthly AWS cost report — example months across scenario timeline
    aws_months = [
        {"month": "2020-03", "scenario": "COVID-19 Impact", "total_usd": 18420, "ec2": 9800, "rds": 3200, "s3": 890, "cloudfront": 430, "support": 500, "other": 3600},
        {"month": "2021-09", "scenario": "Recovery", "total_usd": 24100, "ec2": 12800, "rds": 4100, "s3": 1240, "cloudfront": 680, "support": 500, "other": 4780},
        {"month": "2023-06", "scenario": "Healthy Baseline", "total_usd": 31800, "ec2": 16400, "rds": 5800, "s3": 2100, "cloudfront": 1200, "support": 500, "other": 5800},
        {"month": "2024-01", "scenario": "High Churn Crisis", "total_usd": 38200, "ec2": 19600, "rds": 6800, "s3": 2800, "cloudfront": 1400, "support": 500, "other": 7100},
        {"month": "2024-10", "scenario": "Cybersecurity Breach", "total_usd": 52400, "ec2": 26800, "rds": 8200, "s3": 3400, "cloudfront": 1600, "support": 800, "other": 11600, "incident_surcharge": 4800},
        {"month": "2025-05", "scenario": "Operational Meltdown Recovery", "total_usd": 41200, "ec2": 21400, "rds": 7100, "s3": 3100, "cloudfront": 1500, "support": 500, "other": 7600},
        {"month": "2026-03", "scenario": "Full Recovery", "total_usd": 44800, "ec2": 23200, "rds": 7600, "s3": 3400, "cloudfront": 1700, "support": 500, "other": 8400},
    ]

    write_json(DATA_DIR / "CloudInfra" / "nexacore_aws_monthly_costs.json", {
        "company": "NexaCore Technologies",
        "account_id": "381742956209",
        "region_primary": "us-east-1",
        "region_secondary": "eu-west-1",
        "currency": "USD",
        "reports": aws_months,
        "cost_centers": {
            "Engineering": "0.45",
            "ProductionInfra": "0.35",
            "QA/Staging": "0.12",
            "DataScience": "0.08"
        }
    }, dry_run)

    # EC2 instance inventory
    ec2_instances = [
        {"instance_id": "i-0a1b2c3d4e5f67890", "type": "m6i.2xlarge", "name": "nexacore-api-prod-1", "environment": "production", "monthly_cost_usd": 280, "region": "us-east-1", "launched": "2022-03-15"},
        {"instance_id": "i-0a1b2c3d4e5f67891", "type": "m6i.2xlarge", "name": "nexacore-api-prod-2", "environment": "production", "monthly_cost_usd": 280, "region": "us-east-1", "launched": "2022-03-15"},
        {"instance_id": "i-0a1b2c3d4e5f67892", "type": "m6i.xlarge", "name": "nexacore-api-prod-3", "environment": "production", "monthly_cost_usd": 140, "region": "us-east-1", "launched": "2023-06-01"},
        {"instance_id": "i-0b2c3d4e5f678901", "type": "r6i.2xlarge", "name": "nexacore-db-replica-eu", "environment": "production", "monthly_cost_usd": 420, "region": "eu-west-1", "launched": "2021-11-10"},
        {"instance_id": "i-0c3d4e5f67890123", "type": "c6i.large", "name": "nexacore-worker-1", "environment": "production", "monthly_cost_usd": 85, "region": "us-east-1", "launched": "2023-01-20"},
        {"instance_id": "i-0c3d4e5f67890124", "type": "c6i.large", "name": "nexacore-worker-2", "environment": "production", "monthly_cost_usd": 85, "region": "us-east-1", "launched": "2023-01-20"},
        {"instance_id": "i-0d4e5f6789012345", "type": "t3.medium", "name": "nexacore-staging-api", "environment": "staging", "monthly_cost_usd": 33, "region": "us-east-1", "launched": "2022-09-05"},
        {"instance_id": "i-0e5f678901234567", "type": "t3.large", "name": "nexacore-dev-sandbox", "environment": "development", "monthly_cost_usd": 62, "region": "us-east-1", "launched": "2024-02-14"},
    ]

    write_json(DATA_DIR / "CloudInfra" / "nexacore_ec2_inventory.json", {
        "company": "NexaCore Technologies",
        "exported_at": "2026-06-01T00:00:00Z",
        "instances": ec2_instances,
        "total_monthly_compute_usd": sum(i["monthly_cost_usd"] for i in ec2_instances),
        "utilization_target_pct": 70
    }, dry_run)

    # RDS / Database config
    write_json(DATA_DIR / "CloudInfra" / "nexacore_rds_config.json", {
        "company": "NexaCore Technologies",
        "databases": [
            {
                "identifier": "nexacore-prod-postgres-primary",
                "engine": "PostgreSQL 15.4",
                "instance_class": "db.r6g.2xlarge",
                "storage_gb": 2000,
                "multi_az": True,
                "region": "us-east-1",
                "monthly_cost_usd": 1840,
                "backup_retention_days": 35,
                "encryption": "AES-256",
                "performance_insights": True,
                "read_replicas": ["nexacore-prod-postgres-replica-1", "nexacore-db-replica-eu"]
            },
            {
                "identifier": "nexacore-prod-redis-cluster",
                "engine": "Redis 7.2",
                "instance_class": "cache.r6g.large",
                "cluster_mode": True,
                "nodes": 3,
                "region": "us-east-1",
                "monthly_cost_usd": 480,
                "use_case": "session caching, rate limiting, queue"
            }
        ],
        "monitoring": {
            "cloudwatch_alarms": 24,
            "pagerduty_integration": True,
            "datadog_apm": True
        }
    }, dry_run)

    # Security group and IAM policy snapshot (post-breach remediation)
    write_json(DATA_DIR / "CloudInfra" / "nexacore_security_posture_2024Q4.json", {
        "company": "NexaCore Technologies",
        "audit_date": "2024-10-15",
        "triggered_by": "Post-Incident Security Review (Breach Oct 2024)",
        "findings": [
            {"severity": "CRITICAL", "title": "JWT signing key in plaintext SSM", "status": "REMEDIATED", "remediated_at": "2024-10-02"},
            {"severity": "HIGH", "title": "IMDSv1 enabled on 14 EC2 instances", "status": "REMEDIATED", "remediated_at": "2024-10-04"},
            {"severity": "HIGH", "title": "Overly permissive IAM role on 3 Lambda functions", "status": "IN PROGRESS", "owner": "DevOps Team"},
            {"severity": "MEDIUM", "title": "S3 bucket logging disabled for 2 buckets", "status": "REMEDIATED", "remediated_at": "2024-10-08"},
            {"severity": "MEDIUM", "title": "CloudTrail not enabled in eu-west-1", "status": "REMEDIATED", "remediated_at": "2024-10-06"},
            {"severity": "LOW", "title": "Unused IAM users (8 offboarded employees)", "status": "REMEDIATED", "remediated_at": "2024-10-10"},
        ],
        "vulnerability_counts": {
            "critical": 1,
            "high": 12,
            "medium": 8,
            "low": 23
        },
        "compliance_score_pct": 74.2,
        "target_compliance_score_pct": 95.0,
        "soc2_controls_affected": ["CC6.1", "CC6.2", "CC7.1", "CC7.2", "CC9.2"]
    }, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# INVOICES
# ═══════════════════════════════════════════════════════════════════════════════

def generate_invoices(dry_run: bool) -> None:
    print("\n[Invoices] Generating supplier invoice data...")

    invoices = [
        {
            "invoice_id": "INV-AWS-2024-0312",
            "vendor": "Amazon Web Services, Inc.",
            "vendor_tax_id": "91-1646860",
            "billing_period": "March 2024",
            "issue_date": "2024-04-01",
            "due_date": "2024-04-30",
            "status": "PAID",
            "paid_date": "2024-04-22",
            "currency": "USD",
            "line_items": [
                {"service": "Amazon EC2", "quantity_unit": "instance-hours", "amount_usd": 18420.00},
                {"service": "Amazon RDS (PostgreSQL)", "quantity_unit": "db-hours", "amount_usd": 5840.00},
                {"service": "Amazon S3 Storage", "quantity_unit": "GB-months", "amount_usd": 2140.00},
                {"service": "Amazon CloudFront", "quantity_unit": "requests+data", "amount_usd": 1280.00},
                {"service": "AWS Support (Business)", "quantity_unit": "flat rate", "amount_usd": 500.00},
                {"service": "AWS Secrets Manager", "quantity_unit": "secrets+API calls", "amount_usd": 186.00},
                {"service": "AWS WAF", "quantity_unit": "rules+requests", "amount_usd": 420.00},
            ],
            "subtotal_usd": 28786.00,
            "tax_usd": 0.00,
            "total_usd": 28786.00,
            "cost_center": "Infrastructure / Engineering",
            "approved_by": "Marcus Webb (CFO)",
            "notes": "March spend elevated due to increased traffic from customer success campaign"
        },
        {
            "invoice_id": "INV-SALESFORCE-2024-0401",
            "vendor": "Salesforce, Inc.",
            "vendor_tax_id": "94-3096681",
            "billing_period": "Annual License FY2024-2025",
            "issue_date": "2024-04-01",
            "due_date": "2024-04-30",
            "status": "PAID",
            "paid_date": "2024-04-18",
            "currency": "USD",
            "line_items": [
                {"service": "Salesforce Sales Cloud (Enterprise)", "quantity_unit": "25 licenses × 12mo", "amount_usd": 54000.00},
                {"service": "Salesforce Service Cloud (Professional)", "quantity_unit": "15 licenses × 12mo", "amount_usd": 21600.00},
                {"service": "Salesforce CPQ", "quantity_unit": "12 licenses × 12mo", "amount_usd": 18000.00},
                {"service": "Implementation Support (Premier)", "quantity_unit": "annual", "amount_usd": 12000.00},
            ],
            "subtotal_usd": 105600.00,
            "tax_usd": 0.00,
            "total_usd": 105600.00,
            "cost_center": "Sales / Revenue Operations",
            "approved_by": "Lena Hart (CEO)",
            "notes": "Annual renewal. Negotiated 8% discount from list price."
        },
        {
            "invoice_id": "INV-DATADOG-2024-0901",
            "vendor": "Datadog, Inc.",
            "vendor_tax_id": "47-1228411",
            "billing_period": "September 2024",
            "issue_date": "2024-10-01",
            "due_date": "2024-10-31",
            "status": "PAID",
            "paid_date": "2024-10-28",
            "currency": "USD",
            "line_items": [
                {"service": "Infrastructure Monitoring (Pro)", "quantity_unit": "18 hosts × $18/host", "amount_usd": 3240.00},
                {"service": "APM (Application Performance)", "quantity_unit": "18 hosts × $35/host", "amount_usd": 6300.00},
                {"service": "Log Management (500GB/day)", "quantity_unit": "indexed+ingestion", "amount_usd": 4200.00},
                {"service": "SIEM Security Monitoring", "quantity_unit": "added Oct (prorated)", "amount_usd": 1800.00},
            ],
            "subtotal_usd": 15540.00,
            "tax_usd": 0.00,
            "total_usd": 15540.00,
            "cost_center": "Engineering / SRE",
            "approved_by": "Rafael Gomes (CTO)",
            "notes": "SIEM added post-breach. Budget overrun of $1,800 pre-approved by CFO."
        },
        {
            "invoice_id": "INV-FEDEX-2025-0612",
            "vendor": "FedEx Corporation",
            "vendor_tax_id": "62-1721935",
            "billing_period": "June 2025",
            "issue_date": "2025-07-01",
            "due_date": "2025-07-31",
            "status": "DISPUTED",
            "dispute_reason": "Fuel surcharge applied at incorrect rate (6.4% vs contracted 4.8%)",
            "currency": "USD",
            "line_items": [
                {"service": "Express Freight — US Domestic", "quantity_unit": "48 shipments", "amount_usd": 12400.00},
                {"service": "Express Freight — EU (Paris, Amsterdam)", "quantity_unit": "12 shipments", "amount_usd": 8640.00},
                {"service": "Fuel Surcharge", "quantity_unit": "6.4% of freight (disputed)", "amount_usd": 1345.60},
                {"service": "Dimensional Weight Handling", "quantity_unit": "14 packages >150cm", "amount_usd": 420.00},
            ],
            "subtotal_usd": 22805.60,
            "contracted_fuel_surcharge": 1005.60,
            "overbilled_amount": 340.00,
            "total_usd": 22805.60,
            "cost_center": "Operations / Logistics",
            "approved_by": "Pending resolution",
            "notes": "Procurement team has opened dispute case DISP-FEDEX-2025-0847. Expected credit: $340."
        },
        {
            "invoice_id": "INV-MERCER-2024-0801",
            "vendor": "Mercer LLC",
            "vendor_tax_id": "13-1861413",
            "billing_period": "Compensation Benchmarking Study FY2024",
            "issue_date": "2024-08-01",
            "due_date": "2024-08-31",
            "status": "PAID",
            "paid_date": "2024-08-20",
            "currency": "USD",
            "line_items": [
                {"service": "Global Compensation Survey Participation + Full Data Access", "quantity_unit": "annual subscription", "amount_usd": 24000.00},
                {"service": "Custom Job Family Analysis (Engineering + Product)", "quantity_unit": "42 job codes", "amount_usd": 8400.00},
                {"service": "Executive Compensation Benchmarking", "quantity_unit": "C-suite + VP level (8 roles)", "amount_usd": 6000.00},
                {"service": "Consulting: Comp Structure Redesign Workshop", "quantity_unit": "2 days on-site", "amount_usd": 12000.00},
            ],
            "subtotal_usd": 50400.00,
            "tax_usd": 0.00,
            "total_usd": 50400.00,
            "cost_center": "People / HR",
            "approved_by": "Priya Nair (CHRO) + Lena Hart (CEO)",
            "notes": "Triggered by talent retention crisis. Results showed 38th percentile market positioning — used to justify $480K salary adjustment in Q3."
        },
    ]

    write_json(DATA_DIR / "Invoices" / "nexacore_invoices_2024_2025.json", {
        "company": "NexaCore Technologies",
        "exported_at": "2026-06-01",
        "currency_default": "USD",
        "invoices": invoices,
        "total_paid_usd": sum(i["total_usd"] for i in invoices if i.get("status") == "PAID"),
        "total_disputed_usd": sum(i["total_usd"] for i in invoices if i.get("status") == "DISPUTED"),
    }, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_contracts(dry_run: bool) -> None:
    print("\n[Contracts] Generating supplier and customer contracts...")

    # AWS Enterprise Agreement summary
    write_file(DATA_DIR / "Contracts" / "AWS_Enterprise_Agreement_2023.md", """\
# AWS Enterprise Agreement — NexaCore Technologies
**Contract Reference:** EDP-2023-NXT-00241  
**Effective Date:** January 1, 2023  
**Term:** 3 years (through December 31, 2025)  
**Account Executive:** Jennifer Walsh, AWS (jennifer.walsh@amazon.com)

---

## 1. Parties

**Customer:** NexaCore Technologies, Inc.  
2845 Innovation Drive, Austin TX 78758  
Federal Tax ID: 83-2841620

**Provider:** Amazon Web Services, Inc.  
410 Terry Avenue North, Seattle WA 98109  
Federal Tax ID: 91-1646860

---

## 2. Committed Spend (EDP)

| Year | Annual Commit | Minimum Monthly | Discount Rate |
|------|--------------|-----------------|---------------|
| 2023 | $310,000 | $25,833 | 12% off list |
| 2024 | $390,000 | $32,500 | 14% off list |
| 2025 | $480,000 | $40,000 | 16% off list |

**Undercommit penalty:** 15% of unspent commitment  
**Overcommit:** No penalty; incremental spend at standard rates

---

## 3. Service Credits and SLA

| Service | SLA | Credit Threshold | Credit Rate |
|---------|-----|-----------------|-------------|
| EC2 (individual regions) | 99.99% | <99.95% | 10% monthly bill |
| RDS Multi-AZ | 99.95% | <99.5% | 10% monthly bill |
| S3 | 99.9% | <99.0% | 10% monthly bill |
| CloudFront | 99.9% | <99.0% | 10% monthly bill |

---

## 4. Data Residency and Compliance

- EU customer data: Stored exclusively in eu-west-1 (Dublin, Ireland)
- US customer data: Primary in us-east-1, read replica in us-west-2
- SOC 2 Type II compliance: AWS provides annual report
- GDPR DPA: Executed separately (Ref: GDPR-DPA-2022-NXT-00112)
- HIPAA BAA: Not applicable (NexaCore is not a HIPAA covered entity)

---

## 5. Security Obligations

**AWS obligations:**
- Physical security of data centers
- Hypervisor-level isolation
- Network-level DDoS protection

**NexaCore obligations:**
- Configuration security (EC2 IAM roles, S3 bucket policies)
- Data encryption at rest (AES-256) and in transit (TLS 1.2+)
- Access control and credential management
- Incident response for application-layer breaches

*Note: The October 2024 security incident was a NexaCore-side misconfiguration (SSM plaintext secret), not an AWS infrastructure breach.*

---

## 6. Termination

Either party may terminate with 90 days written notice after the initial 1-year period.  
Early termination by NexaCore: Must pay 100% of remaining annual commit.

---

*Signed by: Marcus Webb (CFO, NexaCore) | Jennifer Walsh (AE, AWS)*  
*Effective: January 1, 2023 | Confidential — Do Not Distribute*
""", dry_run)

    # FedEx Freight Contract
    write_file(DATA_DIR / "Contracts" / "FedEx_Freight_Contract_2024.md", """\
# FedEx Global Freight Agreement — NexaCore Technologies
**Contract Reference:** FDX-NXT-2024-FR-00891  
**Effective Date:** April 1, 2024  
**Term:** 2 years  
**Account Manager:** Carlos Reyes, FedEx Enterprise (c.reyes@fedex.com)

---

## 1. Parties

**Customer:** NexaCore Technologies, Inc.  
Operations Center: 2845 Innovation Drive, Austin TX 78758

**Carrier:** FedEx Corporation  
942 South Shady Grove Road, Memphis TN 38120

---

## 2. Service Scope

- US Domestic Express Freight (Priority Overnight, 2-Day, Ground)
- International Priority Freight (EU destinations: France, Netherlands, Germany, UK)
- Freight management portal: MyFedEx Enterprise (account #38847291)

---

## 3. Pricing & Rates

### US Domestic (FedEx Express)
| Zone | Weight | List Rate | Contracted Rate | Discount |
|------|--------|-----------|-----------------|----------|
| 1-4 | <5 lbs | $18.40 | $13.80 | 25% |
| 1-4 | 5-20 lbs | $28.60 | $20.30 | 29% |
| 5-8 | <5 lbs | $22.80 | $16.85 | 26% |
| 5-8 | 5-20 lbs | $34.20 | $23.95 | 30% |

### EU International
| Destination | Weight Band | Contracted Rate |
|-------------|-------------|-----------------|
| France | <10 kg | $245/shipment |
| Netherlands | <10 kg | $238/shipment |
| Germany | <10 kg | $252/shipment |
| UK (post-Brexit) | <10 kg | $268/shipment |

### Fuel Surcharge
- Applied monthly based on US EIA Weekly Diesel Price Index
- **Contracted cap: 4.8% of freight charges**
- *(Dispute ref DISP-FEDEX-2025-0847: June 2025 invoice applied 6.4% — under resolution)*

---

## 4. Service Level Guarantees

- FedEx Priority Overnight: Money-back guarantee if delivered after 10:30 AM
- 2-Day Express: Money-back guarantee if delivered after end of next business day +1
- Exception: Force majeure events, acts of nature, regulatory delays at customs

---

## 5. Packaging Requirements

NexaCore ships hardware peripherals (IoT sensor units, edge computing modules). Requirements:
- Weight >30 lbs: Must use palletized freight
- Lithium battery declaration: Required for edge units with internal UPS
- Export control (EAR): Some edge computing modules classified ECCN 5A992

---

*Executed by: Rafael Gomes (CTO, NexaCore) | Carlos Reyes (AE, FedEx)*  
*Confidential — NexaCore Procurement*
""", dry_run)

    # Enterprise Customer SLA — anonymized example
    write_file(DATA_DIR / "Contracts" / "Enterprise_Customer_SLA_Template_2024.md", """\
# NexaCore Technologies — Enterprise Customer Service Level Agreement
**Template Version:** 2024.2  
**Effective for accounts:** Enterprise Tier (≥$50K ARR)

---

## 1. Definitions

- **"Platform"**: NexaCore SaaS analytics platform, including all APIs, dashboards, and data pipelines
- **"Downtime"**: Any period where Platform is unavailable or response times exceed 5× normal P99 baseline
- **"Scheduled Maintenance"**: Planned maintenance communicated ≥72 hours in advance

---

## 2. Availability Commitments

| Tier | Monthly Uptime SLA | Credit if Breached |
|------|-------------------|--------------------|
| Standard | 99.5% | 5% of monthly fee per 0.1% below SLA |
| Enterprise | **99.9%** | 10% of monthly fee per 0.1% below SLA |
| Enterprise Plus | 99.95% | 15% of monthly fee per 0.1% below SLA |

**Exclusions:** Scheduled maintenance windows, customer-side network issues, force majeure

*Note: October 2024 breach caused 91.2% uptime over 7-day window. All Enterprise customers received 10% credit for the affected month.*

---

## 3. Support Response Times

| Priority | Definition | First Response | Resolution Target |
|----------|-----------|----------------|-------------------|
| P1 — Critical | Platform unavailable, data loss | **1 hour** (24/7) | 4 hours |
| P2 — High | Major feature unavailable, >20% perf degradation | **4 hours** (business hrs) | 1 business day |
| P3 — Medium | Minor feature impact | **8 hours** | 3 business days |
| P4 — Low | Questions, enhancements | **1 business day** | As scheduled |

*Historical note: During Oct–Dec 2023 churn crisis, P1 response SLA slipped to 11h average. Team restructure + 3 support engineer hires in Q1 2024 restored to <2h average.*

---

## 4. Data Protection

- All customer data encrypted AES-256 at rest and TLS 1.3 in transit
- Data residency options: US (default), EU (available at no extra cost)
- Data retention: 24 months rolling (configurable)
- Backup frequency: Hourly incremental, daily full; 35-day retention
- GDPR DPA available upon request

---

## 5. Credits & Claims Process

- Credits are applied to next invoice cycle
- Must be claimed within 30 days of incident
- Maximum annual credit: 30% of annual contract value
- Credits are sole remedy; no cash refunds

---

*NexaCore Technologies — Enterprise Agreements Team*  
*This template is incorporated by reference into each Master Subscription Agreement*
""", dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# HR DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_hr_docs(dry_run: bool) -> None:
    print("\n[HR] Generating HR records and performance review templates...")

    # Compensation adjustment memo (triggered by talent crisis)
    write_file(DATA_DIR / "HR" / "Compensation_Adjustment_Memo_Q3_2024.md", """\
# INTERNAL MEMORANDUM — CONFIDENTIAL
**To:** All People Managers  
**From:** Priya Nair, CHRO  
**Date:** August 15, 2024  
**Re:** FY2024 Compensation Adjustment — Implementation Guide

---

## Background

Following the Mercer Global Compensation Survey (FY2024) and the talent retention crisis that surfaced in Q2 2024, the Board approved an out-of-cycle compensation adjustment for the Engineering and Product functions.

**Key findings from Mercer analysis:**
- NexaCore engineering compensation sits at **P38 vs. market** (down from P50 in 2022)
- Product management roles: P41 vs. market
- Customer Success: P52 vs. market (acceptable)
- Sales: P61 vs. market (above target — no adjustment)

---

## Scope of Adjustment

| Function | Headcount | Median Increase | Budget Impact |
|----------|-----------|----------------|---------------|
| Software Engineering | 62 | 12.4% | $287,000 |
| Product Management | 14 | 9.8% | $78,000 |
| Data Science | 8 | 11.2% | $42,000 |
| DevOps / SRE | 12 | 13.1% | $73,000 |
| **Total** | **96** | **11.9%** | **$480,000** |

*Note: 18 team members who joined in the last 6 months were already hired at revised market rates and are excluded from the adjustment pool.*

---

## Timeline

| Milestone | Date |
|-----------|------|
| Manager notifications (1:1 conversations) | Aug 19–23, 2024 |
| Employee letters sent | Aug 26, 2024 |
| Adjustment effective date | September 1, 2024 |
| Payroll processing deadline | August 28, 2024 |

---

## Communication Guidelines for Managers

1. **Lead with context**: Reference the Mercer study — "We benchmarked against 500+ tech companies and found our market positioning had drifted."
2. **Do not disclose other individuals' increases** — treat each conversation as confidential
3. **Acknowledge the delay**: "We know this should have happened sooner. We're committed to annual benchmarking going forward."
4. **Equity grants**: Some senior engineers will receive an additional RSU refresh; HR will provide individual guidance

---

## Questions

Contact People Operations: peopleops@nexacore.ai  
HRIS updates will be processed by Payroll — no manager action required

*This document is strictly confidential. Do not forward or share outside your direct reports context.*
""", dry_run)

    # Exit interview analysis
    write_json(DATA_DIR / "HR" / "Q1_2024_Exit_Interview_Analysis.json", {
        "company": "NexaCore Technologies",
        "period": "Q1 2024 (Jan–Mar 2024)",
        "compiled_by": "People Analytics Team",
        "total_voluntary_exits": 23,
        "departments": {
            "Engineering": 9,
            "Customer Success": 6,
            "Sales": 4,
            "Product": 3,
            "Operations": 1
        },
        "primary_exit_reasons": [
            {"reason": "Compensation below market", "pct": 47.8, "count": 11},
            {"reason": "Career growth / promotion velocity", "pct": 26.1, "count": 6},
            {"reason": "Work-life balance / remote policy reversal", "pct": 17.4, "count": 4},
            {"reason": "Manager relationship", "pct": 8.7, "count": 2}
        ],
        "destination_breakdown": [
            {"type": "Competitor (SaaS Analytics)", "pct": 39.1},
            {"type": "Large Tech (FAANG/MAMAA)", "pct": 26.1},
            {"type": "Early-stage startup", "pct": 17.4},
            {"type": "Unknown / declined to share", "pct": 17.4}
        ],
        "regrettable_exits_pct": 78.3,
        "avg_tenure_months": 21.4,
        "nps_final_score": 12,
        "recommendations": [
            "Immediate out-of-cycle comp review for Engineering and Product (priority: P50+ targeting)",
            "Reverse office mandate or provide hybrid flex options",
            "Define and publish updated career ladder with level criteria by Q2",
            "Manager effectiveness training — 3 managers cited in multiple exits"
        ]
    }, dry_run)

    # Hiring plan
    write_json(DATA_DIR / "HR" / "Engineering_Hiring_Plan_H2_2024.json", {
        "company": "NexaCore Technologies",
        "period": "H2 2024 (Jul–Dec)",
        "budget_approved_usd": 620000,
        "headcount_target": 14,
        "roles": [
            {"title": "Senior Software Engineer — Platform", "level": "L5", "team": "Platform Engineering", "priority": "P1", "target_start": "2024-09-01", "comp_range": "$180K–$210K", "status": "OFFER_ACCEPTED"},
            {"title": "Senior Software Engineer — Platform", "level": "L5", "team": "Platform Engineering", "priority": "P1", "target_start": "2024-09-01", "comp_range": "$180K–$210K", "status": "INTERVIEWING"},
            {"title": "Senior Software Engineer — Platform", "level": "L5", "team": "Platform Engineering", "priority": "P1", "target_start": "2024-10-01", "comp_range": "$180K–$210K", "status": "SOURCING"},
            {"title": "Staff Security Engineer", "level": "L6", "team": "Security", "priority": "P1 (post-breach)", "target_start": "2024-10-15", "comp_range": "$220K–$250K", "status": "INTERVIEWING"},
            {"title": "Senior DevOps Engineer", "level": "L5", "team": "Infrastructure", "priority": "P1", "target_start": "2024-10-01", "comp_range": "$175K–$205K", "status": "OFFER_EXTENDED"},
            {"title": "Senior Customer Success Manager", "level": "L5", "team": "Customer Success", "priority": "P1 (churn response)", "target_start": "2024-09-01", "comp_range": "$120K–$145K + commission", "status": "HIRED"},
            {"title": "Senior Customer Success Manager", "level": "L5", "team": "Customer Success", "priority": "P1", "target_start": "2024-09-15", "comp_range": "$120K–$145K + commission", "status": "HIRED"},
            {"title": "Product Manager — Growth", "level": "L4", "team": "Product", "priority": "P2", "target_start": "2024-11-01", "comp_range": "$155K–$180K", "status": "SOURCING"},
            {"title": "Support Engineer (Tier 2)", "level": "L3", "team": "Support", "priority": "P1 (SLA recovery)", "target_start": "2024-09-01", "comp_range": "$95K–$115K", "status": "HIRED"},
            {"title": "Support Engineer (Tier 2)", "level": "L3", "team": "Support", "priority": "P1", "target_start": "2024-09-01", "comp_range": "$95K–$115K", "status": "HIRED"},
            {"title": "Support Engineer (Tier 2)", "level": "L3", "team": "Support", "priority": "P1", "target_start": "2024-10-01", "comp_range": "$95K–$115K", "status": "OFFER_EXTENDED"},
            {"title": "Data Scientist — ML Platform", "level": "L4", "team": "Data Science", "priority": "P2", "target_start": "2024-12-01", "comp_range": "$165K–$195K", "status": "SOURCING"},
        ],
        "avg_time_to_hire_days": 47,
        "target_time_to_hire_days": 35,
        "sourcing_channels": {
            "employee_referral": "34%",
            "linkedin_recruiter": "28%",
            "direct_apply": "22%",
            "agency": "16%"
        }
    }, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# SUPPORT TICKETS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_support_tickets(dry_run: bool) -> None:
    print("\n[Support] Generating support ticket log data...")

    tickets = [
        {
            "ticket_id": "TKT-2024-18441",
            "created_at": "2024-10-02T09:14:22Z",
            "account": "Meridian Financial Partners",
            "tier": "Enterprise",
            "arr_usd": 84000,
            "priority": "P1",
            "category": "Security / Authentication",
            "title": "Users locked out after credential rotation — Cannot authenticate",
            "description": "All users across our organization were force-logged out and are unable to re-authenticate. JWT errors on API calls. Affects 68 users. This is a blocker for our morning reporting run.",
            "first_response_minutes": 14,
            "resolution_minutes": 94,
            "root_cause": "Platform-wide JWT key rotation during security incident (Oct 2024 breach)",
            "resolution": "Customers directed to re-login. New tokens issued. Engineering confirmed new JWT key working.",
            "csat_score": 3,
            "status": "CLOSED",
            "assigned_to": "Sarah Kim (Support)",
            "escalated_to": "Sofia Chen (VP Engineering)"
        },
        {
            "ticket_id": "TKT-2023-11204",
            "created_at": "2023-11-15T14:32:10Z",
            "account": "Clearwater Health Systems",
            "tier": "Enterprise",
            "arr_usd": 120000,
            "priority": "P2",
            "category": "Integration / API",
            "title": "API v2 migration broke our Salesforce connector — data not syncing",
            "description": "After API v2 went live, our custom Salesforce integration stopped pulling opportunity data. Error: 'field_mapping_deprecated' on /api/v2/integrations/crm. We have 3 CSMs relying on this data daily.",
            "first_response_minutes": 380,
            "resolution_minutes": 2880,
            "root_cause": "API v2 changed field schema for CRM connector endpoints without backward compatibility. Breaking change not flagged in migration guide.",
            "resolution": "Provided updated field mapping. Offered white-glove migration call. Bug logged as ENG-4421 for API migration guide update.",
            "csat_score": 2,
            "status": "CLOSED",
            "assigned_to": "Tom Bradley (Support)",
            "escalated_to": "Isabelle Dumont (CPO)",
            "follow_up": "Account flagged as churn risk. CSM assigned."
        },
        {
            "ticket_id": "TKT-2023-11892",
            "created_at": "2023-12-02T10:08:45Z",
            "account": "Apex Logistics Group",
            "tier": "Growth",
            "arr_usd": 28000,
            "priority": "P2",
            "category": "Performance",
            "title": "Dashboard loading times >30 seconds — unusable",
            "description": "Our analytics dashboard takes 28–45 seconds to load for any date range >30 days. Other customers must be affected too. This is a daily workflow for our ops team.",
            "first_response_minutes": 520,
            "resolution_minutes": 14400,
            "root_cause": "PostgreSQL query without index on large accounts. Compound query on KPI table scanning 4.8M rows for accounts with >18 months of data.",
            "resolution": "Engineering added composite index (ENG-4389). Immediate improvement from 28s → 1.8s for affected query. Deployed hotfix Dec 4.",
            "csat_score": 4,
            "status": "CLOSED",
            "assigned_to": "Dana Osei (Support)"
        },
        {
            "ticket_id": "TKT-2024-21003",
            "created_at": "2024-11-08T08:41:00Z",
            "account": "Brightline Capital",
            "tier": "Enterprise",
            "arr_usd": 196000,
            "priority": "P3",
            "category": "Feature Request",
            "title": "Request: Slack integration for anomaly alerts",
            "description": "We have 4 analysts who need real-time Slack notifications when an anomaly is detected. Currently we check the dashboard manually. Competitor X has this. This is a renewal risk for us — our contract is up in April.",
            "first_response_minutes": 240,
            "resolution_minutes": None,
            "root_cause": None,
            "resolution": "Feature request logged as PRD-892. PM confirmed Q2 2025 delivery. Account flagged as strategic — CSM to share roadmap preview.",
            "csat_score": 4,
            "status": "CLOSED — Feature Tracked",
            "assigned_to": "Rachel Torres (Support)",
            "product_ticket": "PRD-892",
            "renewal_risk": True
        },
    ]

    write_json(DATA_DIR / "Support" / "nexacore_support_tickets_2023_2024.json", {
        "company": "NexaCore Technologies",
        "period": "2023-01 to 2024-12",
        "system": "Zendesk Enterprise",
        "stats": {
            "total_tickets": 4812,
            "p1_tickets": 34,
            "p1_avg_first_response_hours": 2.1,
            "p1_avg_resolution_hours": 8.4,
            "overall_csat": 72,
            "sla_breach_rate_pct": 18.2
        },
        "sample_tickets": tickets,
        "top_categories": [
            {"category": "Integration / API", "pct": 28.4},
            {"category": "Performance", "pct": 21.8},
            {"category": "Feature Request", "pct": 18.2},
            {"category": "Authentication / Access", "pct": 14.6},
            {"category": "Data / Reporting", "pct": 12.3},
            {"category": "Billing", "pct": 4.7}
        ]
    }, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# PROCUREMENT / PURCHASE ORDERS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_procurement(dry_run: bool) -> None:
    print("\n[Procurement] Generating purchase orders and RFP data...")

    pos = [
        {
            "po_number": "PO-2024-0483",
            "vendor": "Aruba Networks (HPE)",
            "category": "IT Infrastructure",
            "description": "Network equipment refresh — HQ Austin office",
            "items": [
                {"item": "Aruba 6300F 48G Switch", "qty": 4, "unit_price_usd": 3840, "total_usd": 15360},
                {"item": "Aruba AP-615 Access Points", "qty": 24, "unit_price_usd": 680, "total_usd": 16320},
                {"item": "Aruba Central License (3yr)", "qty": 28, "unit_price_usd": 245, "total_usd": 6860},
                {"item": "Installation & Professional Services", "qty": 1, "unit_price_usd": 8400, "total_usd": 8400}
            ],
            "total_usd": 46940,
            "approved_by": "Rafael Gomes (CTO)",
            "budget_code": "CAPEX-IT-2024-Q2",
            "status": "RECEIVED",
            "po_date": "2024-05-02",
            "delivery_date": "2024-06-15"
        },
        {
            "po_number": "PO-2024-0521",
            "vendor": "Flex Ltd. (Contract Manufacturing)",
            "category": "Hardware / COGS",
            "description": "IoT Edge Compute Module — Q3 2024 production run (Model NXT-EC-300)",
            "items": [
                {"item": "NXT-EC-300 Edge Compute Module", "qty": 500, "unit_price_usd": 218, "total_usd": 109000},
                {"item": "Custom PCB Assembly", "qty": 500, "unit_price_usd": 44, "total_usd": 22000},
                {"item": "Quality Inspection (IPC-A-610D)", "qty": 1, "unit_price_usd": 6800, "total_usd": 6800},
                {"item": "Packaging + Labeling", "qty": 500, "unit_price_usd": 12, "total_usd": 6000}
            ],
            "total_usd": 143800,
            "approved_by": "Lena Hart (CEO)",
            "budget_code": "COGS-HW-2024-Q3",
            "status": "PARTIAL_DELIVERY",
            "po_date": "2024-07-10",
            "scheduled_delivery": "2024-09-30",
            "delivery_status": "320 of 500 units delivered. 180 units delayed — Flex citing component shortage for NVIDIA Jetson Nano module.",
            "delay_impact": "Delayed 6 enterprise deployments. Logistics OTD metric impacted in Q3 2025."
        },
        {
            "po_number": "PO-2025-0112",
            "vendor": "HashiCorp (now IBM)",
            "category": "Software / Security",
            "description": "HashiCorp Vault Enterprise — secrets management (post-breach remediation)",
            "items": [
                {"item": "Vault Enterprise License (3 clusters, 3yr)", "qty": 1, "unit_price_usd": 84000, "total_usd": 84000},
                {"item": "Professional Services — Implementation", "qty": 15, "unit_price_usd": 2400, "total_usd": 36000},
                {"item": "Vault Training (online, 10 engineers)", "qty": 10, "unit_price_usd": 1800, "total_usd": 18000}
            ],
            "total_usd": 138000,
            "approved_by": "Marcus Webb (CFO) + Rafael Gomes (CTO)",
            "budget_code": "OPEX-SECURITY-2024-EMERGENCY",
            "status": "ACTIVE",
            "po_date": "2024-11-01",
            "notes": "Emergency budget approved by Board as part of $240K post-breach security remediation. Replaces manual SSM Parameter Store management."
        }
    ]

    write_json(DATA_DIR / "Procurement" / "nexacore_purchase_orders_2024_2025.json", {
        "company": "NexaCore Technologies",
        "currency": "USD",
        "purchase_orders": pos,
        "total_committed_usd": sum(p["total_usd"] for p in pos),
        "categories": {
            "IT Infrastructure (CAPEX)": 46940,
            "Hardware COGS": 143800,
            "Software / Security (OPEX)": 138000
        }
    }, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# EMAILS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_emails(dry_run: bool) -> None:
    print("\n[Emails] Generating executive email samples...")

    write_file(DATA_DIR / "Emails" / "CFO_to_CEO_Cash_Runway_Feb2024.md", """\
**From:** Marcus Webb <mwebb@nexacore.ai>  
**To:** Lena Hart <lhart@nexacore.ai>  
**Date:** February 16, 2024, 07:42 AM  
**Subject:** [URGENT] Cash position — need to discuss before board meeting  
**Classification:** CONFIDENTIAL — DO NOT FORWARD

---

Lena,

Can we grab 30 minutes today? I want to walk through the updated cash model before we finalize the board deck.

Quick summary so you have context going in:

**Current cash:** $8.4M  
**Current monthly burn:** ~$920K (up from $840K in November due to unplanned CS headcount)  
**Runway at current burn:** ~9 months (November 2024)  

The Norwest term sheet looks good — $15M at a $48M pre-money. If we close by May, we extend runway to 24+ months and can execute the comp adjustment + 3 support hires without sweating the P&L.

But I want to stress-test the "no raise" scenario:
- If we accelerate the efficiency targets from Q3 to Q2, we can get burn to $780K/month
- That extends runway to 11 months — still yellow, not green
- We'd have to pause the comp adjustment and slow hiring

My recommendation: Don't delay the raise. The churn situation makes a raise harder to close if NRR keeps declining — we need to get the term sheet signed while the market is receptive to our growth story (28% YoY ARR is still strong).

I've updated Slide 14 and 15 in the board deck to show both scenarios. Want me to have Elena prep a 1-pager for each board member?

Let me know if you're free 10–10:30 AM.

Marcus
""", dry_run)

    write_file(DATA_DIR / "Emails" / "CTO_Engineering_Lead_PostBreach_Oct2024.md", """\
**From:** Rafael Gomes <rgomes@nexacore.ai>  
**To:** Engineering Leadership Team (DL: eng-leads@nexacore.ai)  
**Date:** October 3, 2024, 11:15 PM  
**Subject:** Incident post-mortem kickoff + no-blame policy  
**Classification:** INTERNAL

---

Team,

We've got full service back up as of 14:00 UTC today. I know it's been an exhausting 78 hours and I want to personally thank every one of you who was involved in the response. Sofia, Michael, Ana, Dev team — exceptional work under pressure.

I want to set the tone for what comes next:

**Post-mortem**
We're doing a full blameless post-mortem. The AWS SSM misconfiguration was a process failure — a gap in our secret rotation enforcement that nobody on the team was specifically accountable for. That's a systems problem, not a people problem. Nobody loses their job over a missed checklist.

The post-mortem doc is in Confluence (link below). I want:
- A complete 5-whys timeline by Monday
- All contributing factors (not just root cause) documented
- Specific process changes proposed — not just "be more careful"

**What I need from leads**
Each team lead please add your section by EOD Saturday. Sofia will compile and publish internally by October 15.

**No external communication**
Legal and comms have the customer notifications handled. Please don't discuss incident details outside your immediate team. If a customer asks you directly, direct them to support.

**Mental health note**
Incident response is genuinely hard. If anyone needs to take a day to decompress after this week, that's entirely fine. Reach out to your lead or to People Ops.

More details in the All-Hands deck I'll share Monday.

Thank you all,
Rafael

---
Post-mortem doc: confluence.nexacore.ai/x/ENG-INCIDENT-OCT2024
""", dry_run)

    write_file(DATA_DIR / "Emails" / "CPO_PM_Team_ChurnCrisis_Nov2023.md", """\
**From:** Isabelle Dumont <idumont@nexacore.ai>  
**To:** Product Management Team (DL: product@nexacore.ai)  
**CC:** Lena Hart <lhart@nexacore.ai>  
**Date:** November 28, 2023, 04:58 PM  
**Subject:** Q4 product priorities — retention over growth  
**Classification:** INTERNAL

---

Team,

After today's sprint review and the churn numbers Marcus shared, I want to reframe our priorities for the rest of Q4 and all of Q1.

We are in a retention crisis. Monthly churn hit 4.1% in October. If we don't bend that curve by March, we'll miss our ARR target by $3.2M and the Series B story gets significantly harder to tell.

**Immediate reprioritization (effective next sprint):**

OUT for Q4:
- Mobile app redesign (pushed to Q3 2024)
- Advanced analytics v2 (pushed to Q2 2024)
- API marketplace (pushed to Q3 2024)

IN for Q4–Q1:
1. **API v2 migration guide + backward compat layer** — Engineering and Product joint sprint. The broken Salesforce connectors are a churn driver.
2. **In-app health score + early warning** — Give customers visibility into their own engagement metrics so they self-serve before churning.
3. **Slack/Teams integration** — This is literally on our exit interview list. Competitors have it. We build it.
4. **P1/P2 support response restoration** — We're at 11h avg P1 response. Our SLA says 4h. Every breach is a churn signal.

I'm not sugarcoating this: Q4 is defense, not offense. We protect the ARR base first.

Each PM: Please update your Q4 roadmap items in Productboard by Thursday EOD. I'll review Friday morning.

Isabelle
""", dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# BOARD REPORTS (Markdown — to be converted to PDF separately)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_board_reports(dry_run: bool) -> None:
    print("\n[BoardReports] Generating quarterly board reports...")

    write_file(DATA_DIR / "BoardReports" / "Q3_2025_Operational_Recovery_Report.md", """\
# NexaCore Technologies — Q3 2025 Operational Recovery Report
**Period:** July 1 – September 30, 2025  
**Prepared by:** Office of the CEO  
**Distribution:** Board of Directors — Confidential

---

## Executive Summary

Q3 2025 marks the beginning of NexaCore's recovery from the compound crises of 2024 (high customer churn, talent attrition, cybersecurity breach) and Q1–Q2 2025 (operational meltdown and logistics disruption). While full recovery is not yet complete, leading indicators are trending positively across all seven domains.

**ARR:** $94.2M (Q3 2025 run-rate) vs. $88.1M trough in Q1 2025 — +6.9% recovery  
**Monthly Churn:** 2.1% (down from 5.4% peak in Feb 2024)  
**System Uptime:** 99.4% (recovery from 91.2% breach nadir)  
**OEE:** 74.2% (up from 57.5% meltdown low in Q1 2025)  
**Logistics OTD:** 88.4% (up from 68% Q1 2025 low)

---

## Domain Performance vs. Targets

### Finance
| Metric | Q3 2025 | Target | vs. Target |
|--------|---------|--------|------------|
| ARR ($M) | 94.2 | 96.0 | -1.9% |
| Gross Margin | 68.8% | 70% | -1.2pp |
| EBITDA Margin | -2.1% | +1% | -3.1pp |
| Cash Runway | 18.2 months | 18+ months | ✅ |

*Series B ($15M, closed April 2024) secured runway. Conservative spending maintained through recovery period.*

### Growth (Customer)
| Metric | Q3 2025 | Target | vs. Target |
|--------|---------|--------|------------|
| Monthly Churn | 2.1% | ≤1.5% | ⚠️ Above target |
| NRR | 102% | 108% | ⚠️ Below target |
| LTV:CAC | 2.2x | ≥3.0x | ⚠️ Below target |
| NPS | 48 | ≥55 | ⚠️ Trending up |

*Churn recovery ahead of internal model (projected 2.5% by Q3). LTV:CAC improving as CAC reduces post-reorg.*

### People
| Metric | Q3 2025 | Target | vs. Target |
|--------|---------|--------|------------|
| Voluntary Turnover | 14.2% TTM | ≤13% | ⚠️ Near target |
| Time-to-Hire (Eng) | 38 days | ≤35 days | ⚠️ Close |
| eNPS | +31 | ≥+35 | ⚠️ Recovering |
| Open Critical Roles | 4 | ≤3 | ⚠️ |

*Comp adjustment effective Sep 2024 showing impact: turnover down from 27% peak. eNPS recovering.*

### IT
| Metric | Q3 2025 | Target | vs. Target |
|--------|---------|--------|------------|
| Uptime | 99.4% | ≥99.5% | ⚠️ 0.1pp miss |
| MTTR (P0) | 2.8h | ≤4h | ✅ |
| Critical CVEs open | 2 | ≤3 | ✅ |
| Vault Adoption | 94% secrets migrated | 100% | ⚠️ |

*Security posture dramatically improved post-breach. Vault implementation 94% complete.*

### Operations
| Metric | Q3 2025 | Target | vs. Target |
|--------|---------|--------|------------|
| OEE | 74.2% | ≥75% | ⚠️ Near target |
| Defect Rate | 2.1% | ≤2.0% | ⚠️ |
| Throughput | 1,840 units/day | 1,900 | ⚠️ |
| Scrap Cost | $82K/mo | ≤$75K | ⚠️ |

*OEE recovering strongly from 57.5% meltdown low. Root cause (Flex component shortage) fully resolved Q2 2025.*

### Logistics
| Metric | Q3 2025 | Target | vs. Target |
|--------|---------|--------|------------|
| OTD | 88.4% | ≥92% | ⚠️ |
| Order Cycle Time | 6.8 days | ≤6.0 days | ⚠️ |
| Freight Cost/Unit | $34.20 | ≤$32.00 | ⚠️ |
| Perfect Order Rate | 91.2% | ≥95% | ⚠️ |

*Freight costs elevated due to post-meltdown expedited shipments. Returning to standard rates Q4.*

### ESG
| Metric | Q3 2025 | Target | vs. Target |
|--------|---------|--------|------------|
| Scope 1+2 (tCO₂e) | 294 | ≤280 | ⚠️ |
| Renewable Energy % | 68% | 75% | ⚠️ |
| Waste Diversion | 78.4% | ≥80% | ⚠️ |
| Employee Safety (TRIR) | 0.4 | ≤0.5 | ✅ |

*EU operations (Amsterdam office) achieved 100% renewable energy in Q3.*

---

## Outlook — Q4 2025 and Full Recovery

Full recovery to pre-crisis baseline metrics expected: **Q2 2026** for most domains.  
Projected FY2026 ARR: **$108–$112M** (pending Q4 churn performance).

The Slack/Teams integration launch (October 15) is expected to reduce feature-gap churn by 30–40 basis points.

---

*Prepared by: Office of the CEO | NexaCore Technologies | Confidential — Board Distribution Only*
""", dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# LEGAL
# ═══════════════════════════════════════════════════════════════════════════════

def generate_legal(dry_run: bool) -> None:
    print("\n[Legal] Generating legal and compliance documents...")

    write_file(DATA_DIR / "Legal" / "GDPR_Breach_Notification_Oct2024.md", """\
# GDPR Personal Data Breach Notification
**Article 33 — Notification to Supervisory Authority**

**Filed by:** NexaCore Technologies, Inc. (EU Establishment: NexaCore Europe B.V., Herengracht 458, 1017CA Amsterdam, Netherlands)  
**DPO Contact:** privacy@nexacore.ai  
**Supervisory Authority:** Autoriteit Persoonsgegevens (Dutch DPA)  
**Filed:** October 1, 2024 (within 72-hour GDPR window)  
**Reference:** GDPR-BREACH-2024-NXT-001

---

## 1. Nature of the Breach

**Incident date/time:** September 28, 2024, 03:47 UTC (first alert)  
**Breach type:** Unauthorized access to read-only audit log data via compromised authentication token  
**Duration:** Approximately 48 hours (03:47 UTC Sep 28 to 06:00 UTC Sep 28, containment; forensics until Oct 2)

**Systems involved:**
- NexaCore SaaS platform authentication microservice (AWS us-east-1)
- Read-only audit log database (Neon PostgreSQL, read replica)

---

## 2. Categories and Approximate Number of Data Subjects

| Category | Count | Nationality |
|----------|-------|-------------|
| EU enterprise account admins (audit log entries) | 47 | FR (23), NL (14), DE (8), BE (2) |
| EU individual users (session tokens, now expired) | 284 | FR, NL, DE, BE |
| **Total EU data subjects** | **331** | |

**Types of data potentially accessed:**
- Account IDs (internal UUIDs, not real names)
- Email addresses (used as account identifiers, visible in audit logs)
- Timestamps of API calls
- IP addresses of API requests

**Data NOT accessed:**
- Financial data, payment information
- Passwords (hashed + salted, not stored in audit logs)
- Personal health, ethnicity, or sensitive category data (not processed)
- Customer content/documents

---

## 3. Likely Consequences

Risk assessment: **MEDIUM**  
Basis: Email addresses and account activity metadata were potentially accessed. No financial or sensitive category data was involved. Account IDs are not linked to real-world identity without NexaCore's internal mapping tables (not accessed).

---

## 4. Measures Taken

**Containment (Sep 28):**
- Compromised JWT signing key rotated within 2 hours of detection
- All 2,400 active sessions force-expired and invalidated
- Affected EC2 instance isolated from network

**Notification:**
- 331 EU data subjects notified by email October 1, 2024
- EU enterprise account contacts notified by phone October 1, 2024

**Remediation:**
- IMDSv2 enforced fleet-wide (Oct 4)
- All secrets migrated to encrypted SSM + HashiCorp Vault program started
- External security assessment commissioned (NCC Group, Q1 2025)

---

## 5. DPO Certification

I certify this notification is accurate to the best of NexaCore's knowledge as of the filing date.

**Data Protection Officer:** Dr. Emma van der Berg  
**Filed:** October 1, 2024  
**Reference:** GDPR-BREACH-2024-NXT-001

---

*Confidential — Legal Team + DPO Only*
""", dry_run)

    write_json(DATA_DIR / "Legal" / "vendor_ndas_registry.json", {
        "company": "NexaCore Technologies",
        "registry_updated": "2026-06-01",
        "ndas": [
            {"counterparty": "Mercer LLC", "type": "Mutual NDA", "signed": "2024-07-15", "expires": "2027-07-15", "scope": "Compensation benchmarking engagement", "owner": "People Ops"},
            {"counterparty": "NCC Group (External Pen Test)", "type": "Mutual NDA", "signed": "2024-12-01", "expires": "2026-12-01", "scope": "Penetration testing engagement Q1 2025", "owner": "Security"},
            {"counterparty": "Norwest Venture Partners", "type": "Mutual NDA", "signed": "2023-11-10", "expires": "2025-11-10", "scope": "Series B fundraise", "owner": "Finance"},
            {"counterparty": "Flex Ltd.", "type": "Mutual NDA", "signed": "2022-04-01", "expires": "2028-04-01", "scope": "Contract manufacturing — NXT-EC edge compute modules", "owner": "Operations"},
            {"counterparty": "Pilot Acquisition Target A (Undisclosed)", "type": "One-way (NexaCore receives)", "signed": "2026-01-15", "expires": "2027-01-15", "scope": "M&A due diligence", "owner": "Corporate Development — CONFIDENTIAL"},
        ]
    }, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

GENERATORS = {
    "cloud_infra": generate_cloud_infra,
    "invoices": generate_invoices,
    "contracts": generate_contracts,
    "hr": generate_hr_docs,
    "support": generate_support_tickets,
    "procurement": generate_procurement,
    "emails": generate_emails,
    "board_reports": generate_board_reports,
    "legal": generate_legal,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="NexaCore Enterprise Data Generator")
    parser.add_argument("--type", choices=list(GENERATORS.keys()), help="Generate only one data type")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()

    print("=" * 65)
    print("NexaCore Technologies — Enterprise Data Generator")
    print(f"Output directory: {DATA_DIR}")
    if args.dry_run:
        print("[DRY RUN MODE — no files will be written]")
    print("=" * 65)

    if args.type:
        GENERATORS[args.type](args.dry_run)
    else:
        for name, gen in GENERATORS.items():
            gen(args.dry_run)

    print("\n✅ Done.")
    if not args.dry_run:
        # Count files
        total = sum(1 for _ in DATA_DIR.rglob("*") if _.is_file() and _.suffix not in {".py", ".pyc"})
        print(f"   Total data files in {DATA_DIR.relative_to(DATA_DIR.parent.parent)}: {total}")


if __name__ == "__main__":
    main()
