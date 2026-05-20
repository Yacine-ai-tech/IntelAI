#!/usr/bin/env python3
# Enhanced Dataset Generator for OMNINTELOS
# Generates 1600+ KPI records across 10 companies, 5 domains, 2015-2026
# Includes: Financial statements, PDFs, images, emails, sheets, JSON, webhooks

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None

# Configuration
OUTPUT_DIR = Path("enhanced_synthetic_dataset")
PDF_DIR = OUTPUT_DIR / "pdf"
CSV_DIR = OUTPUT_DIR / "csv"
IMG_DIR = OUTPUT_DIR / "images"
JSON_DIR = OUTPUT_DIR / "json"
EMAIL_DIR = OUTPUT_DIR / "emails"
SHEETS_DIR = OUTPUT_DIR / "sheets_exports"

for d in [PDF_DIR, CSV_DIR, IMG_DIR, JSON_DIR, EMAIL_DIR, SHEETS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

NUM_COMPANIES = 10
NUM_MONTHS = 12 * (2026 - 2015 + 1)
START_DATE = datetime(2015, 1, 1)

COMPANIES = [
    {"name": "CloudSync Pro", "sector": "SaaS"},
    {"name": "DataFlow Analytics", "sector": "Data"},
    {"name": "HealthCare Analytics", "sector": "HealthTech"},
    {"name": "SecureShield Corp", "sector": "Cybersecurity"},
    {"name": "SolarTech Innovations", "sector": "GreenEnergy"},
    {"name": "NeuralNet Labs", "sector": "AI/ML"},
    {"name": "EduPlatform Pro", "sector": "EdTech"},
    {"name": "LendingTree Digital", "sector": "Fintech"},
    {"name": "ServerLess Tech", "sector": "Cloud"},
    {"name": "CarePath Digital", "sector": "HealthTech"},
]

KPI_TEMPLATES = {
    "Finance": {
        "revenue": {"start": 500000, "growth": 1.25, "volatility": 0.15},
        "gross_margin": {"start": 0.60, "growth": 1.02, "volatility": 0.08},
        "ebitda": {"start": 100000, "growth": 1.30, "volatility": 0.20},
        "operating_expenses": {"start": 250000, "growth": 1.12, "volatility": 0.10},
        "cash_on_hand": {"start": 300000, "growth": 1.15, "volatility": 0.25},
    },
    "Growth": {
        "mrr": {"start": 50000, "growth": 1.20, "volatility": 0.10},
        "arr": {"start": 600000, "growth": 1.22, "volatility": 0.12},
        "churn_rate": {"start": 0.08, "growth": 0.95, "volatility": 0.05},
        "nps": {"start": 35, "growth": 1.03, "volatility": 8},
    },
    "Operations": {
        "efficiency_rate": {"start": 0.75, "growth": 1.02, "volatility": 0.05},
        "cycle_time_days": {"start": 10, "growth": 0.98, "volatility": 1},
        "on_time_delivery": {"start": 0.92, "growth": 1.01, "volatility": 0.03},
    },
    "People": {
        "headcount": {"start": 15, "growth": 1.18, "volatility": 0.3},
        "turnover_rate": {"start": 0.15, "growth": 0.92, "volatility": 0.05},
        "engagement_score": {"start": 65, "growth": 1.02, "volatility": 5},
    },
    "ESG": {
        "carbon_intensity": {"start": 10, "growth": 0.92, "volatility": 1},
        "renewable_energy_pct": {"start": 0.20, "growth": 1.15, "volatility": 0.10},
        "safety_incidents": {"start": 2, "growth": 0.88, "volatility": 1},
    },
}


def generate_time_series(start_value, growth_rate, volatility, num_periods, floor=0):
    values = [start_value]
    for _ in range(num_periods - 1):
        noise = np.random.normal(0, volatility * values[-1])
        next_val = values[-1] * growth_rate + noise
        values.append(max(floor, next_val))
    return values


def add_anomalies(values, anomaly_rate=0.05):
    modified = values.copy()
    num_anomalies = int(len(modified) * anomaly_rate)
    for _ in range(num_anomalies):
        idx = random.randint(0, len(modified) - 1)
        shock = random.uniform(0.7, 1.4)
        modified[idx] *= shock
    return modified


def generate_kpi_data():
    records = []
    
    for company in COMPANIES:
        for domain, kpis in KPI_TEMPLATES.items():
            for kpi_name, config in kpis.items():
                values = generate_time_series(config["start"], config["growth"], 
                                             config["volatility"], NUM_MONTHS)
                values = add_anomalies(values)
                
                for i, value in enumerate(values):
                    date = START_DATE + timedelta(days=30 * i)
                    records.append({
                        "company": company["name"],
                        "sector": company["sector"],
                        "domain": domain,
                        "metric": kpi_name,
                        "value": max(0, value),
                        "period": date.strftime("%Y-%m"),
                        "date": date.isoformat(),
                    })
    
    df = pd.DataFrame(records)
    csv_path = CSV_DIR / "all_kpis.csv"
    df.to_csv(csv_path, index=False)
    print("[OK] Generated {} KPI records".format(len(df)))
    return df


def generate_financial_statements():
    for company in COMPANIES:
        for year in range(2024, 2027):
            pl_data = {
                "company": company["name"],
                "year": year,
                "revenue": random.uniform(1000000, 50000000),
                "cogs": random.uniform(300000, 15000000),
                "opex": random.uniform(200000, 10000000),
            }
            
            pl_data["gross_profit"] = pl_data["revenue"] - pl_data["cogs"]
            pl_data["ebitda"] = pl_data["gross_profit"] - pl_data["opex"]
            pl_data["net_income"] = pl_data["ebitda"] * 0.79
            
            bs_data = {
                "company": company["name"],
                "year": year,
                "assets": random.uniform(5000000, 100000000),
                "liabilities": random.uniform(1000000, 30000000),
            }
            bs_data["equity"] = bs_data["assets"] - bs_data["liabilities"]
            
            fin_data = {"p_l": pl_data, "balance_sheet": bs_data}
            json_path = JSON_DIR / "{}_{}_fin.json".format(company["name"].replace(" ", "_"), year)
            with open(json_path, "w") as f:
                json.dump(fin_data, f, indent=2)
    
    print("[OK] Generated financial statements")


def generate_pdf_documents():
    if not FPDF:
        print("[SKIP] fpdf not available")
        return
    
    for company in COMPANIES[:3]:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "INVOICE - {}".format(company["name"]), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, "Date: {}".format(datetime.now().strftime("%Y-%m-%d")), ln=True)
        pdf.cell(0, 10, "Amount: ${:.2f}".format(random.uniform(5000, 50000)), ln=True)
        
        pdf_path = PDF_DIR / "{}_inv.pdf".format(company["name"].replace(" ", "_"))
        pdf.output(str(pdf_path))
    
    print("[OK] Generated PDF documents")


def generate_images():
    if not Image or not ImageDraw:
        print("[SKIP] PIL not available")
        return
    
    for i in range(5):
        img = Image.new("RGB", (400, 300), color="white")
        draw = ImageDraw.Draw(img)
        for x in range(50, 350):
            y = 250 - random.randint(20, 200)
            y2 = 250 - random.randint(20, 200)
            draw.line([(x, y), (x+1, y2)], fill="blue", width=2)
        
        img_path = IMG_DIR / "chart_{}.png".format(i)
        img.save(img_path)
    
    print("[OK] Generated sample images")


def generate_email_samples():
    for company in COMPANIES:
        emails = []
        for subject in ["Revenue Report", "Team Update", "Efficiency Alert"]:
            email = {
                "from": "reports@{}.com".format(company["name"].lower().replace(" ", "")),
                "to": "insights@company.com",
                "subject": subject,
                "body": "Data for {}".format(company["name"]),
                "date": datetime.now().isoformat(),
            }
            emails.append(email)
        
        email_path = EMAIL_DIR / "{}_emails.json".format(company["name"].replace(" ", "_"))
        with open(email_path, "w") as f:
            json.dump(emails, f, indent=2)
    
    print("[OK] Generated email samples")


def generate_sheets_exports():
    for company in COMPANIES[:5]:
        sheets_data = {}
        
        kpis = []
        for domain in list(KPI_TEMPLATES.keys())[:2]:
            for metric in list(KPI_TEMPLATES[domain].keys())[:2]:
                kpis.append({
                    "Domain": domain,
                    "Metric": metric,
                    "Value": random.uniform(10000, 1000000),
                })
        sheets_data["KPIs"] = kpis
        
        sheets_path = SHEETS_DIR / "{}_sheet.json".format(company["name"].replace(" ", "_"))
        with open(sheets_path, "w") as f:
            json.dump(sheets_data, f, indent=2)
    
    print("[OK] Generated Sheets exports")


def generate_n8n_webhooks():
    payloads = []
    
    for company in COMPANIES[:3]:
        for domain in list(KPI_TEMPLATES.keys())[:2]:
            metrics = KPI_TEMPLATES[domain]
            metric_name = list(metrics.keys())[0]
            
            payload = {
                "company": company["name"],
                "domain": domain,
                "metric": metric_name,
                "value": random.uniform(1000, 1000000),
                "timestamp": datetime.now().isoformat(),
            }
            payloads.append(payload)
    
    webhook_path = JSON_DIR / "n8n_payloads.json"
    with open(webhook_path, "w") as f:
        json.dump(payloads, f, indent=2)
    
    print("[OK] Generated N8N webhook payloads")


def generate_domain_configs():
    for domain in KPI_TEMPLATES.keys():
        config = {
            "domain": domain,
            "metrics": list(KPI_TEMPLATES[domain].keys()),
        }
        config_path = JSON_DIR / "{}_cfg.json".format(domain.lower())
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    
    print("[OK] Generated domain configs")


def main():
    print("\n" + "=" * 70)
    print("OMNINTELOS ENHANCED DATASET GENERATOR")
    print("=" * 70)
    print("\nGenerating comprehensive test data:")
    print("  - {} companies".format(len(COMPANIES)))
    print("  - {} months (2015 to 2026)".format(NUM_MONTHS))
    print("  - {} domains".format(len(KPI_TEMPLATES)))
    print("  - Multiple formats: CSV, PDF, JSON, Email, Sheets\n")
    
    generate_kpi_data()
    generate_financial_statements()
    generate_pdf_documents()
    generate_images()
    generate_email_samples()
    generate_sheets_exports()
    generate_n8n_webhooks()
    generate_domain_configs()
    
    print("\n" + "=" * 70)
    print("SUCCESS: Dataset generation complete!")
    print("=" * 70)
    print("\nOutput: enhanced_synthetic_dataset/")
    print("  - 1600+ KPI records")
    print("  - Financial statements")
    print("  - PDFs, images, emails, sheets")
    print("  - N8N webhooks")
    print("\nReady for comprehensive platform testing!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
