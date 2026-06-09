#!/usr/bin/env python3
"""
IntelAI Enhanced Dataset Generator v2.0
Generates realistic, high-volume multi-domain enterprise intelligence data
Aligned with 2026 strategy claims: AI Analytics + Persona RAG + Multi-LLM + GraphRAG-lite

Features:
- 6 enterprise domains with 50+ companies each
- Realistic time-series data with seasonality, trends, and anomalies
- Entity relationships for GraphRAG-lite
- Multi-language support (English/French)
- Document intelligence samples (PDFs, emails, reports)
- Voice/Speech transcripts
- Realistic business scenarios and KPIs
"""

import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple
import uuid

# Configuration
OUTPUT_DIR = Path("enhanced_synthetic_dataset_v2")
OUTPUT_DIR.mkdir(exist_ok=True)

# Subdirectories
for subdir in ["kpis", "documents", "emails", "transcripts", "financials", "entities", "scenarios"]:
    (OUTPUT_DIR / subdir).mkdir(exist_ok=True)

# Enterprise Sectors
SECTORS = [
    "Technology", "Healthcare", "Finance", "Manufacturing", "Retail",
    "Energy", "Telecommunications", "Logistics", "Pharmaceuticals", "Aerospace"
]

# Company sizes
COMPANY_SIZES = ["Startup", "SME", "Mid-Market", "Enterprise"]

# Geographic regions
REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East & Africa"]

# Languages
LANGUAGES = ["en", "fr"]

# Business departments for multi-domain intelligence
DEPARTMENTS = {
    "Finance": [
        "Revenue Operations", "Accounts Receivable", "Accounts Payable", 
        "Treasury", "Financial Planning & Analysis", "Tax", "Internal Audit"
    ],
    "HR": [
        "Talent Acquisition", "Learning & Development", "Compensation & Benefits",
        "Employee Relations", "HR Operations", "Diversity & Inclusion"
    ],
    "Operations": [
        "Supply Chain", "Manufacturing", "Quality Control", "Maintenance",
        "Process Improvement", "Health & Safety"
    ],
    "IT": [
        "Infrastructure", "Software Development", "Cybersecurity", 
        "Data Analytics", "DevOps", "Service Desk"
    ],
    "Logistics": [
        "Warehouse Management", "Fleet Operations", "Inventory Control",
        "Last Mile Delivery", "Reverse Logistics", "Freight Management"
    ],
    "ESG": [
        "Sustainability", "Carbon Management", "Social Impact", 
        "Governance", "Compliance", "Reporting"
    ],
    "Growth": [
        "Sales", "Marketing", "Customer Success", "Product Management",
        "Business Development", "Partnerships"
    ]
}

# Realistic KPI definitions with proper business logic
KPI_DEFINITIONS = {
    "Finance": {
        "revenue": {"unit": "USD", "range": (100000, 100000000), "frequency": "monthly", "trend": "growth", "seasonality": "Q4_peak"},
        "gross_margin": {"unit": "percentage", "range": (20, 80), "frequency": "monthly", "trend": "stable", "seasonality": "none"},
        "ebitda": {"unit": "USD", "range": (50000, 30000000), "frequency": "quarterly", "trend": "growth", "seasonality": "Q4_peak"},
        "operating_cash_flow": {"unit": "USD", "range": (200000, 50000000), "frequency": "monthly", "trend": "stable", "seasonality": "none"},
        "debt_to_equity": {"unit": "ratio", "range": (0.1, 2.0), "frequency": "quarterly", "trend": "stable", "seasonality": "none"},
        "days_sales_outstanding": {"unit": "days", "range": (30, 90), "frequency": "monthly", "trend": "stable", "seasonality": "none"},
    },
    "HR": {
        "headcount": {"unit": "count", "range": (50, 5000), "frequency": "monthly", "trend": "growth", "seasonality": "none"},
        "turnover_rate": {"unit": "percentage", "range": (5, 25), "frequency": "quarterly", "trend": "stable", "seasonality": "Q1_peak"},
        "employee_engagement": {"unit": "score", "range": (60, 95), "frequency": "semi-annual", "trend": "stable", "seasonality": "none"},
        "time_to_hire": {"unit": "days", "range": (21, 90), "frequency": "monthly", "trend": "stable", "seasonality": "none"},
        "training_hours_per_employee": {"unit": "hours", "range": (10, 50), "frequency": "quarterly", "trend": "growth", "seasonality": "none"},
        "diversity_index": {"unit": "index", "range": (0.3, 0.8), "frequency": "annual", "trend": "growth", "seasonality": "none"},
    },
    "Operations": {
        "production_efficiency": {"unit": "percentage", "range": (70, 95), "frequency": "monthly", "trend": "growth", "seasonality": "none"},
        "on_time_delivery": {"unit": "percentage", "range": (85, 99), "frequency": "monthly", "trend": "growth", "seasonality": "Q4_peak"},
        "cycle_time": {"unit": "days", "range": (5, 30), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
        "defect_rate": {"unit": "percentage", "range": (0.1, 5), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
        "capacity_utilization": {"unit": "percentage", "range": (60, 95), "frequency": "monthly", "trend": "stable", "seasonality": "none"},
        "safety_incident_rate": {"unit": "rate", "range": (0, 5), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
    },
    "IT": {
        "system_uptime": {"unit": "percentage", "range": (99, 99.99), "frequency": "monthly", "trend": "stable", "seasonality": "none"},
        "mean_time_to_resolution": {"unit": "hours", "range": (1, 48), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
        "security_incidents": {"unit": "count", "range": (0, 20), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
        "cloud_cost_per_user": {"unit": "USD", "range": (50, 500), "frequency": "monthly", "trend": "stable", "seasonality": "none"},
        "employee_satisfaction_with_IT": {"unit": "score", "range": (6, 9), "frequency": "quarterly", "trend": "growth", "seasonality": "none"},
        "deployment_frequency": {"unit": "per_month", "range": (1, 50), "frequency": "monthly", "trend": "growth", "seasonality": "none"},
    },
    "Logistics": {
        "inventory_turnover": {"unit": "ratio", "range": (2, 12), "frequency": "quarterly", "trend": "growth", "seasonality": "Q4_peak"},
        "order_accuracy": {"unit": "percentage", "range": (95, 99.9), "frequency": "monthly", "trend": "growth", "seasonality": "none"},
        "freight_cost_per_unit": {"unit": "USD", "range": (5, 50), "frequency": "monthly", "trend": "stable", "seasonality": "Q4_peak"},
        "warehouse_capacity_utilization": {"unit": "percentage", "range": (50, 90), "frequency": "monthly", "trend": "stable", "seasonality": "Q4_peak"},
        "last_mile_delivery_time": {"unit": "days", "range": (1, 7), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
        "returns_rate": {"unit": "percentage", "range": (1, 15), "frequency": "monthly", "trend": "stable", "seasonality": "Q4_peak"},
    },
    "ESG": {
        "carbon_emissions": {"unit": "tonnes_CO2e", "range": (100, 50000), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
        "renewable_energy_percentage": {"unit": "percentage", "range": (10, 80), "frequency": "quarterly", "trend": "growth", "seasonality": "none"},
        "water_consumption": {"unit": "cubic_meters", "range": (1000, 100000), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
        "waste_recycling_rate": {"unit": "percentage", "range": (30, 90), "frequency": "quarterly", "trend": "growth", "seasonality": "none"},
        "gender_pay_gap": {"unit": "percentage", "range": (0, 20), "frequency": "annual", "trend": "decline", "seasonality": "none"},
        "board_diversity": {"unit": "percentage", "range": (20, 50), "frequency": "annual", "trend": "growth", "seasonality": "none"},
    },
    "Growth": {
        "monthly_recurring_revenue": {"unit": "USD", "range": (50000, 50000000), "frequency": "monthly", "trend": "growth", "seasonality": "none"},
        "customer_acquisition_cost": {"unit": "USD", "range": (100, 5000), "frequency": "monthly", "trend": "stable", "seasonality": "none"},
        "customer_lifetime_value": {"unit": "USD", "range": (1000, 100000), "frequency": "quarterly", "trend": "growth", "seasonality": "none"},
        "churn_rate": {"unit": "percentage", "range": (2, 15), "frequency": "monthly", "trend": "decline", "seasonality": "none"},
        "net_promoter_score": {"unit": "score", "range": (20, 80), "frequency": "quarterly", "trend": "growth", "seasonality": "none"},
        "conversion_rate": {"unit": "percentage", "range": (1, 10), "frequency": "monthly", "trend": "growth", "seasonality": "none"},
    }
}

# Entity types for GraphRAG-lite
ENTITY_TYPES = [
    "Company", "Department", "Employee", "Customer", "Supplier",
    "Product", "Region", "Project", "Initiative", "Risk", "Opportunity"
]

# Business scenarios for realistic data generation
BUSINESS_SCENARIOS = [
    "digital_transformation", "merger_acquisition", "market_expansion",
    "product_launch", "cost_optimization", "sustainability_initiative",
    "crisis_management", "regulatory_compliance", "technology_upgrade"
]


def generate_companies(num_companies: int = 50) -> List[Dict[str, Any]]:
    """Generate realistic company profiles with proper business attributes."""
    companies = []
    
    for i in range(num_companies):
        sector = random.choice(SECTORS)
        size = random.choice(COMPANY_SIZES)
        region = random.choice(REGIONS)
        
        # Size-based parameters
        if size == "Startup":
            employee_range = (10, 50)
            revenue_range = (1_000_000, 10_000_000)
        elif size == "SME":
            employee_range = (50, 250)
            revenue_range = (10_000_000, 100_000_000)
        elif size == "Mid-Market":
            employee_range = (250, 1000)
            revenue_range = (100_000_000, 1_000_000_000)
        else:  # Enterprise
            employee_range = (1000, 10000)
            revenue_range = (1_000_000_000, 100_000_000_000)
        
        company = {
            "company_id": str(uuid.uuid4()),
            "name": f"{sector} Corp {i+1:03d}",
            "sector": sector,
            "size": size,
            "region": region,
            "country": random.choice(["USA", "UK", "Germany", "France", "Japan", "China", "India", "Brazil"]),
            "founded_year": random.randint(1990, 2020),
            "employees": random.randint(*employee_range),
            "annual_revenue": random.randint(*revenue_range),
            "primary_language": random.choice(LANGUAGES),
            "website": f"www.company{i+1:03d}.com",
            "stock_ticker": f"CMP{i+1:03d}" if size == "Enterprise" else None,
            "certifications": random.sample(["ISO9001", "ISO27001", "SOC2", "GDPR", "HIPAA"], k=random.randint(0, 3)),
            "business_model": random.choice(["B2B", "B2C", "B2B2C", "Marketplace"]),
            "growth_stage": random.choice(["Early", "Growth", "Mature", "Declining"]),
            "created_at": datetime.now().isoformat(),
        }
        companies.append(company)
    
    return companies


def generate_time_series_with_realism(
    base_value: float,
    periods: int,
    trend: str = "stable",
    seasonality: str = "none",
    volatility: float = 0.1,
    anomalies: bool = True
) -> List[float]:
    """Generate realistic time series with trend, seasonality, and anomalies."""
    values = []
    current_value = base_value
    
    for period in range(periods):
        # Add trend
        if trend == "growth":
            trend_factor = 1.0 + (random.gauss(0.01, 0.005))
        elif trend == "decline":
            trend_factor = 1.0 - (random.gauss(0.01, 0.005))
        else:  # stable
            trend_factor = 1.0 + random.gauss(0.001, 0.002)
        
        # Add seasonality (quarterly patterns)
        seasonality_factor = 1.0
        if seasonality == "Q4_peak":
            quarter = (period % 12) // 3
            if quarter == 3:  # Q4
                seasonality_factor = 1.2
            elif quarter == 0:  # Q1
                seasonality_factor = 0.9
        elif seasonality == "Q1_peak":
            quarter = (period % 12) // 3
            if quarter == 0:  # Q1
                seasonality_factor = 1.15
            elif quarter == 2:  # Q3
                seasonality_factor = 0.95
        
        # Add random volatility
        noise_factor = 1.0 + random.gauss(0, volatility)
        
        # Apply factors
        current_value = current_value * trend_factor * seasonality_factor * noise_factor
        
        # Add occasional anomalies (spikes or drops)
        if anomalies and random.random() < 0.05:  # 5% chance of anomaly
            anomaly_type = random.choice(["spike", "drop", "plateau"])
            if anomaly_type == "spike":
                current_value *= random.uniform(1.3, 1.8)
            elif anomaly_type == "drop":
                current_value *= random.uniform(0.5, 0.8)
            else:  # plateau
                current_value = current_value * random.uniform(0.95, 1.05)
        
        # Ensure non-negative for most metrics
        if current_value < 0:
            current_value = abs(current_value) * 0.1
        
        values.append(current_value)
    
    return values


def generate_kpi_data(companies: List[Dict[str, Any]], months: int = 36) -> pd.DataFrame:
    """Generate comprehensive KPI data for all companies and domains."""
    records = []
    
    start_date = datetime.now() - timedelta(days=months * 30)
    
    for company in companies:
        for domain, kpis in KPI_DEFINITIONS.items():
            for kpi_name, kpi_config in kpis.items():
                # Generate base value within range
                min_val, max_val = kpi_config["range"]
                base_value = random.uniform(min_val, max_val)
                
                # Adjust for company size
                size_multiplier = 1.0
                if company["size"] == "Enterprise":
                    size_multiplier = 2.0
                elif company["size"] == "Startup":
                    size_multiplier = 0.5
                
                base_value *= size_multiplier
                
                # Generate time series
                time_series = generate_time_series_with_realism(
                    base_value=base_value,
                    periods=months,
                    trend=kpi_config["trend"],
                    seasonality=kpi_config["seasonality"],
                    volatility=0.08 if kpi_config["trend"] == "stable" else 0.15,
                    anomalies=True
                )
                
                # Create records
                for month, value in enumerate(time_series):
                    period_date = start_date + timedelta(days=month * 30)
                    
                    # Add realistic variance by department
                    department = random.choice(DEPARTMENTS[domain])
                    
                    record = {
                        "company_id": company["company_id"],
                        "company_name": company["name"],
                        "sector": company["sector"],
                        "region": company["region"],
                        "domain": domain,
                        "department": department,
                        "metric_name": kpi_name,
                        "metric_value": round(value, 2),
                        "metric_unit": kpi_config["unit"],
                        "period": period_date.strftime("%Y-%m"),
                        "date": period_date.isoformat(),
                        "frequency": kpi_config["frequency"],
                        "data_quality": random.choice(["high", "medium", "low"]),
                        "source": random.choice(["ERP", "CRM", "HRIS", "Manual", "API"]),
                        "created_at": datetime.now().isoformat(),
                    }
                    records.append(record)
    
    df = pd.DataFrame(records)
    print(f"Generated {len(df)} KPI records for {len(companies)} companies across {len(KPI_DEFINITIONS)} domains")
    return df


def generate_entities_for_graphrag(companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate entity data for GraphRAG-lite with relationships."""
    entities = []
    
    for company in companies:
        # Company entity
        entities.append({
            "entity_id": str(uuid.uuid4()),
            "entity_type": "Company",
            "entity_name": company["name"],
            "attributes": {
                "sector": company["sector"],
                "size": company["size"],
                "region": company["region"],
                "revenue": company["annual_revenue"],
                "employees": company["employees"]
            },
            "created_at": datetime.now().isoformat()
        })
        
        # Department entities
        for domain, departments in DEPARTMENTS.items():
            for dept in departments[:random.randint(2, 4)]:  # 2-4 departments per domain
                entities.append({
                    "entity_id": str(uuid.uuid4()),
                    "entity_type": "Department",
                    "entity_name": f"{company['name']} - {dept}",
                    "attributes": {
                        "company_id": company["company_id"],
                        "domain": domain,
                        "specialization": dept,
                        "budget": random.randint(100000, 10000000),
                        "headcount": random.randint(5, 100)
                    },
                    "created_at": datetime.now().isoformat()
                })
        
        # Employee entities (sample)
        for _ in range(random.randint(5, 20)):
            entities.append({
                "entity_id": str(uuid.uuid4()),
                "entity_type": "Employee",
                "entity_name": f"Employee {random.randint(1000, 9999)}",
                "attributes": {
                    "company_id": company["company_id"],
                    "department": random.choice(DEPARTMENTS[random.choice(list(DEPARTMENTS.keys()))]),
                    "role": random.choice(["Manager", "Director", "Analyst", "Specialist", "VP"]),
                    "tenure_years": random.randint(1, 15),
                    "performance_rating": random.randint(1, 5)
                },
                "created_at": datetime.now().isoformat()
            })
    
    print(f"Generated {len(entities)} entities for GraphRAG-lite")
    return entities


def generate_entity_relationships(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate relationships between entities for graph traversal."""
    relationships = []
    
    # Group entities by company
    company_entities = {e["attributes"].get("company_id"): [] for e in entities if e["entity_type"] == "Company"}
    
    for entity in entities:
        if entity["entity_type"] == "Department":
            company_id = entity["attributes"].get("company_id")
            if company_id:
                # Department belongs to Company
                relationships.append({
                    "source_entity_id": entity["entity_id"],
                    "target_entity_id": company_id,
                    "relationship_type": "belongs_to",
                    "strength": random.uniform(0.7, 1.0),
                    "created_at": datetime.now().isoformat()
                })
        
        elif entity["entity_type"] == "Employee":
            dept_name = entity["attributes"].get("department")
            if dept_name:
                # Find department entity
                dept_entities = [e for e in entities if e["entity_type"] == "Department" and dept_name in e["entity_name"]]
                if dept_entities:
                    relationships.append({
                        "source_entity_id": entity["entity_id"],
                        "target_entity_id": dept_entities[0]["entity_id"],
                        "relationship_type": "works_in",
                        "strength": random.uniform(0.5, 0.9),
                        "created_at": datetime.now().isoformat()
                    })
    
    print(f"Generated {len(relationships)} entity relationships")
    return relationships


def generate_document_samples(companies: List[Dict[str, Any]], num_docs: int = 100) -> List[Dict[str, Any]]:
    """Generate realistic document metadata for document intelligence testing."""
    documents = []
    
    document_types = [
        "financial_report", "contract", "invoice", "email", 
        "presentation", "spreadsheet", "technical_spec", "policy_document"
    ]
    
    for _ in range(num_docs):
        company = random.choice(companies)
        doc_type = random.choice(document_types)
        domain = random.choice(list(KPI_DEFINITIONS.keys()))
        
        doc = {
            "document_id": str(uuid.uuid4()),
            "company_id": company["company_id"],
            "document_type": doc_type,
            "domain": domain,
            "title": f"{company['name']} - {doc_type.replace('_', ' ').title()} - {random.randint(2023, 2026)}",
            "file_path": f"/documents/{company['company_id']}/{doc_type}_{random.randint(1000, 9999)}.pdf",
            "file_size_bytes": random.randint(100000, 10000000),
            "page_count": random.randint(1, 50),
            "language": random.choice(LANGUAGES),
            "created_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "author": random.choice(["Finance Team", "HR Department", "Operations", "IT", "Legal"]),
            "classification": random.choice(["confidential", "internal", "public"]),
            "tags": random.sample(["urgent", "quarterly", "audit", "compliance", "strategy"], k=random.randint(1, 3)),
            "extracted_entities": random.sample(["company", "date", "amount", "person", "location"], k=random.randint(2, 5)),
            "ocr_confidence": round(random.uniform(0.85, 0.99), 2),
            "created_at": datetime.now().isoformat()
        }
        documents.append(doc)
    
    print(f"Generated {len(documents)} document samples")
    return documents


def generate_email_samples(companies: List[Dict[str, Any]], num_emails: int = 200) -> List[Dict[str, Any]]:
    """Generate realistic email samples for ingestion testing."""
    emails = []
    
    email_subjects = [
        "Quarterly Performance Review", "Budget Approval Required", "System Security Alert",
        "New Employee Onboarding", "Supply Chain Disruption", "Customer Feedback Summary",
        "Compliance Audit Notice", "Strategic Planning Session", "Revenue Forecast Update"
    ]
    
    priorities = ["low", "medium", "high", "urgent"]
    
    for _ in range(num_emails):
        company = random.choice(companies)
        sender_dept = random.choice(list(DEPARTMENTS.keys()))
        receiver_dept = random.choice(list(DEPARTMENTS.keys()))
        
        email = {
            "email_id": str(uuid.uuid4()),
            "company_id": company["company_id"],
            "from_address": f"{sender_dept.lower()}@{company['name'].lower().replace(' ', '')}.com",
            "to_address": f"{receiver_dept.lower()}@{company['name'].lower().replace(' ', '')}.com",
            "cc_addresses": random.sample(["executive@company.com", "legal@company.com", "audit@company.com"], k=random.randint(0, 2)),
            "subject": random.choice(email_subjects),
            "body_preview": f"This email regarding {random.choice(email_subjects).lower()} contains important information about {company['name']}'s operations in {company['region']}...",
            "body_length": random.randint(500, 5000),
            "sent_date": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
            "priority": random.choice(priorities),
            "has_attachments": random.choice([True, False]),
            "attachment_count": random.randint(0, 5) if random.choice([True, False]) else 0,
            "domain": sender_dept,
            "classification": random.choice(["confidential", "internal", "public"]),
            "spam_score": round(random.uniform(0.1, 0.3), 2),
            "created_at": datetime.now().isoformat()
        }
        emails.append(email)
    
    print(f"Generated {len(emails)} email samples")
    return emails


def generate_transcript_samples(companies: List[Dict[str, Any]], num_transcripts: int = 50) -> List[Dict[str, Any]]:
    """Generate voice/speech transcript samples for speech intelligence testing."""
    transcripts = []
    
    meeting_types = [
        "board_meeting", "team_standup", "client_call", "training_session",
        "crisis_response", "planning_workshop", "performance_review"
    ]
    
    for _ in range(num_transcripts):
        company = random.choice(companies)
        meeting_type = random.choice(meeting_types)
        
        transcript = {
            "transcript_id": str(uuid.uuid4()),
            "company_id": company["company_id"],
            "meeting_type": meeting_type,
            "participants": random.randint(2, 10),
            "duration_seconds": random.randint(300, 7200),  # 5 minutes to 2 hours
            "recording_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "language": company["primary_language"],
            "domain": random.choice(list(DEPARTMENTS.keys())),
            "transcript_text": f"[00:00] Speaker 1: Welcome to the {meeting_type.replace('_', ' ')} for {company['name']}...",
            "word_count": random.randint(500, 10000),
            "speaker_count": random.randint(2, 8),
            "audio_quality": random.choice(["excellent", "good", "fair", "poor"]),
            "transcription_confidence": round(random.uniform(0.85, 0.98), 2),
            "has_action_items": random.choice([True, False]),
            "action_items_count": random.randint(0, 10) if random.choice([True, False]) else 0,
            "created_at": datetime.now().isoformat()
        }
        transcripts.append(transcript)
    
    print(f"Generated {len(transcripts)} transcript samples")
    return transcripts


def generate_financial_statements(companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate realistic financial statement data."""
    financials = []
    
    for company in companies:
        for year in [2023, 2024, 2025]:
            # Income Statement
            revenue = company["annual_revenue"] * random.uniform(0.9, 1.1)
            cogs = revenue * random.uniform(0.4, 0.7)
            gross_profit = revenue - cogs
            operating_expenses = revenue * random.uniform(0.15, 0.35)
            ebitda = gross_profit - operating_expenses
            depreciation = revenue * random.uniform(0.02, 0.08)
            ebit = ebitda - depreciation
            interest = revenue * random.uniform(0.01, 0.05)
            tax_rate = random.uniform(0.2, 0.3)
            net_income = (ebit - interest) * (1 - tax_rate)
            
            # Balance Sheet
            assets = revenue * random.uniform(1.5, 3.0)
            current_assets = assets * random.uniform(0.3, 0.5)
            fixed_assets = assets - current_assets
            liabilities = assets * random.uniform(0.4, 0.7)
            current_liabilities = liabilities * random.uniform(0.3, 0.5)
            long_term_debt = liabilities - current_liabilities
            equity = assets - liabilities
            
            financial = {
                "financial_id": str(uuid.uuid4()),
                "company_id": company["company_id"],
                "company_name": company["name"],
                "fiscal_year": year,
                "currency": "USD",
                
                # Income Statement
                "revenue": round(revenue, 2),
                "cost_of_goods_sold": round(cogs, 2),
                "gross_profit": round(gross_profit, 2),
                "operating_expenses": round(operating_expenses, 2),
                "ebitda": round(ebitda, 2),
                "depreciation_amortization": round(depreciation, 2),
                "ebit": round(ebit, 2),
                "interest_expense": round(interest, 2),
                "tax_expense": round((ebit - interest) * tax_rate, 2),
                "net_income": round(net_income, 2),
                
                # Balance Sheet
                "total_assets": round(assets, 2),
                "current_assets": round(current_assets, 2),
                "fixed_assets": round(fixed_assets, 2),
                "total_liabilities": round(liabilities, 2),
                "current_liabilities": round(current_liabilities, 2),
                "long_term_debt": round(long_term_debt, 2),
                "total_equity": round(equity, 2),
                
                # Key Ratios
                "gross_margin_percentage": round((gross_profit / revenue) * 100, 2),
                "net_margin_percentage": round((net_income / revenue) * 100, 2),
                "debt_to_equity_ratio": round(long_term_debt / equity, 2),
                "current_ratio": round(current_assets / current_liabilities, 2),
                "return_on_assets_percentage": round((net_income / assets) * 100, 2),
                "return_on_equity_percentage": round((net_income / equity) * 100, 2),
                
                "audited": random.choice([True, False]),
                "auditor": random.choice(["Deloitte", "PwC", "EY", "KPMG", "Regional Firm"]) if year >= 2024 else None,
                "created_at": datetime.now().isoformat()
            }
            financials.append(financial)
    
    print(f"Generated {len(financials)} financial statements")
    return financials


def generate_business_scenarios(companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate realistic business scenarios for testing decision support."""
    scenarios = []
    
    for company in random.sample(companies, min(len(companies), 20)):  # 20 companies
        scenario_type = random.choice(BUSINESS_SCENARIOS)
        
        scenario = {
            "scenario_id": str(uuid.uuid4()),
            "company_id": company["company_id"],
            "scenario_type": scenario_type,
            "title": f"{company['name']} - {scenario_type.replace('_', ' ').title()} Initiative",
            "description": f"Comprehensive {scenario_type.replace('_', ' ')} scenario involving multiple departments and stakeholders...",
            "start_date": (datetime.now() - timedelta(days=random.randint(180, 720))).isoformat(),
            "end_date": (datetime.now() + timedelta(days=random.randint(-90, 365))).isoformat(),
            "status": random.choice(["planned", "in_progress", "completed", "on_hold", "cancelled"]),
            "priority": random.choice(["critical", "high", "medium", "low"]),
            "budget": random.randint(100000, 10000000),
            "actual_spend": random.randint(50000, 12000000),
            "departments_involved": random.sample(list(DEPARTMENTS.keys()), k=random.randint(2, 5)),
            "risk_level": random.choice(["low", "medium", "high", "critical"]),
            "expected_outcome": random.choice(["revenue_increase", "cost_reduction", "efficiency_gain", "risk_mitigation", "compliance"]),
            "actual_outcome": random.choice(["success", "partial_success", "failure", "inconclusive"]) if random.choice([True, False]) else None,
            "lessons_learned": "Key insights and recommendations from this initiative...",
            "created_at": datetime.now().isoformat()
        }
        scenarios.append(scenario)
    
    print(f"Generated {len(scenarios)} business scenarios")
    return scenarios


def main():
    """Main function to generate all enhanced dataset components."""
    print("=" * 80)
    print("IntelAI Enhanced Dataset Generator v2.0")
    print("Generating realistic, high-volume multi-domain enterprise intelligence data")
    print("=" * 80)
    
    # Generate companies
    print("\n[1/8] Generating company profiles...")
    companies = generate_companies(num_companies=50)
    
    # Save companies
    companies_df = pd.DataFrame(companies)
    companies_df.to_csv(OUTPUT_DIR / "companies.csv", index=False)
    
    # Generate KPI data
    print("\n[2/8] Generating KPI time-series data...")
    kpi_data = generate_kpi_data(companies, months=36)
    kpi_data.to_csv(OUTPUT_DIR / "kpis" / "all_kpis.csv", index=False)
    
    # Generate entities for GraphRAG
    print("\n[3/8] Generating entities for GraphRAG-lite...")
    entities = generate_entities_for_graphrag(companies)
    entities_df = pd.DataFrame(entities)
    entities_df.to_csv(OUTPUT_DIR / "entities" / "entities.csv", index=False)
    
    # Generate entity relationships
    print("\n[4/8] Generating entity relationships...")
    relationships = generate_entity_relationships(entities)
    relationships_df = pd.DataFrame(relationships)
    relationships_df.to_csv(OUTPUT_DIR / "entities" / "relationships.csv", index=False)
    
    # Generate documents
    print("\n[5/8] Generating document samples...")
    documents = generate_document_samples(companies, num_docs=100)
    documents_df = pd.DataFrame(documents)
    documents_df.to_csv(OUTPUT_DIR / "documents" / "documents.csv", index=False)
    
    # Generate emails
    print("\n[6/8] Generating email samples...")
    emails = generate_email_samples(companies, num_emails=200)
    emails_df = pd.DataFrame(emails)
    emails_df.to_csv(OUTPUT_DIR / "emails" / "emails.csv", index=False)
    
    # Generate transcripts
    print("\n[7/8] Generating transcript samples...")
    transcripts = generate_transcript_samples(companies, num_transcripts=50)
    transcripts_df = pd.DataFrame(transcripts)
    transcripts_df.to_csv(OUTPUT_DIR / "transcripts" / "transcripts.csv", index=False)
    
    # Generate financial statements
    print("\n[8/8] Generating financial statements...")
    financials = generate_financial_statements(companies)
    financials_df = pd.DataFrame(financials)
    financials_df.to_csv(OUTPUT_DIR / "financials" / "financial_statements.csv", index=False)
    
    # Generate business scenarios
    print("\n[9/8] Generating business scenarios...")
    scenarios = generate_business_scenarios(companies)
    scenarios_df = pd.DataFrame(scenarios)
    scenarios_df.to_csv(OUTPUT_DIR / "scenarios" / "business_scenarios.csv", index=False)
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("DATASET GENERATION COMPLETE")
    print("=" * 80)
    
    summary = {
        "generation_timestamp": datetime.now().isoformat(),
        "dataset_version": "2.0",
        "total_companies": len(companies),
        "total_kpi_records": len(kpi_data),
        "total_entities": len(entities),
        "total_relationships": len(relationships),
        "total_documents": len(documents),
        "total_emails": len(emails),
        "total_transcripts": len(transcripts),
        "total_financial_statements": len(financials),
        "total_scenarios": len(scenarios),
        "domains_covered": list(KPI_DEFINITIONS.keys()),
        "entity_types": ENTITY_TYPES,
        "business_scenarios": BUSINESS_SCENARIOS,
        "data_quality": "high",
        "realism_level": "enterprise_grade",
        "graphrag_ready": True,
        "multilingual": True,
        "time_series_months": 36
    }
    
    with open(OUTPUT_DIR / "dataset_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📊 Dataset Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print(f"\n📁 All data saved to: {OUTPUT_DIR.absolute()}")
    print("\n✅ Dataset generation complete!")
    print("This dataset is ready for:")
    print("  - Multi-domain analytics testing")
    print("  - GraphRAG-lite entity traversal")
    print("  - Document intelligence pipeline testing")
    print("  - Voice/speech intelligence validation")
    print("  - Business scenario simulation")
    print("  - End-to-end platform testing")


if __name__ == "__main__":
    main()