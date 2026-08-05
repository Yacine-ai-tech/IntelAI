#!/usr/bin/env python3
import csv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import numpy as np

OUTPUT_DIR = "/home/ai-sniper/Downloads/credential/IntelAI/data"

START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2026, 6, 1)

def get_months():
    months = []
    current = START_DATE
    while current <= END_DATE:
        months.append(current.strftime("%Y-%m"))
        current += relativedelta(months=1)
    return months

MONTHS = get_months() # 78 months

def get_month_index(date_str):
    return MONTHS.index(date_str)

SCENARIOS = [
    ("2020-01", "2021-06", "COVID"),
    ("2021-07", "2022-12", "Recovery"),
    ("2023-01", "2023-09", "Healthy"),
    ("2023-10", "2024-03", "Churn crisis"),
    ("2024-04", "2024-09", "Talent crisis"),
    ("2024-10", "2025-03", "Cyber breach"),
    ("2025-04", "2025-09", "Ops meltdown"),
    ("2025-10", "2026-06", "Full Recovery")
]

class MetricSeries:
    def __init__(self, name, base_value, unit, direction):
        self.name = name
        self.base_value = base_value
        self.unit = unit
        self.direction = direction
        self.values = [base_value] * len(MONTHS)
        self.targets = {} # target multiplier at end of a scenario
    
    def set_target(self, scenario_end, multiplier):
        self.targets[scenario_end] = multiplier
    
    def set_target_absolute(self, scenario_end, value):
        self.targets[scenario_end] = value / self.base_value if self.base_value != 0 else value

    def calculate(self):
        # We start at base_value in 2019-12 (index -1)
        current_val = self.base_value
        current_idx = -1
        
        for start_month, end_month, name in SCENARIOS:
            start_idx = get_month_index(start_month)
            end_idx = get_month_index(end_month)
            
            if name in self.targets:
                target_val = self.base_value * self.targets[name]
            elif end_month in self.targets:
                target_val = self.base_value * self.targets[end_month]
            else:
                target_val = self.base_value # revert to base

            # Special case for Growth NRR / Churn
            # Linear interpolation from current_val to target_val over (end_idx - start_idx + 1) months
            steps = end_idx - start_idx + 1
            if steps > 0:
                step_val = (target_val - current_val) / steps
                for i in range(start_idx, end_idx + 1):
                    self.values[i] = current_val + step_val * (i - start_idx + 1)
            
            current_val = self.values[end_idx]

        # Apply specific monthly growths if any
        if self.name == "Revenue (USD)":
            healthy_start = get_month_index("2023-01")
            healthy_end = get_month_index("2023-09")
            for i in range(healthy_start, healthy_end + 1):
                if i == healthy_start:
                    self.values[i] = self.values[i-1] * 1.02
                else:
                    self.values[i] = self.values[i-1] * 1.02
            # re-anchor current_val for subsequent scenarios
            current_val = self.values[healthy_end]
            # re-calculate rest of the timeline to account for the new baseline
            for start_month, end_month, name in SCENARIOS:
                start_idx = get_month_index(start_month)
                if start_idx <= healthy_end: continue
                end_idx = get_month_index(end_month)
                target_val = self.base_value * self.targets.get(name, 1.0)
                # But revenue grew, so target_val should scale based on the new baseline? 
                # Prompt says: "Revenue x0.91" during churn crisis. We will multiply current_val by 0.91
                if name == "Churn crisis":
                    target_val = current_val * 0.91
                elif name == "Cyber breach":
                    target_val = current_val * 0.88
                else:
                    target_val = current_val
                
                steps = end_idx - start_idx + 1
                if steps > 0:
                    step_val = (target_val - current_val) / steps
                    for i in range(start_idx, end_idx + 1):
                        self.values[i] = current_val + step_val * (i - start_idx + 1)
                current_val = self.values[end_idx]
                
        if self.name == "Carbon Footprint tCO2e (metric tons)":
            # declining 4% YoY is roughly 0.33% per month
            for i in range(len(MONTHS)):
                if i > 0:
                    self.values[i] = self.values[i] * (0.9967 ** i)


def generate_domain_csv(domain, metrics, category, source):
    os.makedirs(os.path.join(OUTPUT_DIR, domain), exist_ok=True)
    filename = os.path.join(OUTPUT_DIR, domain, f"nexacore_{domain.lower()}_kpis.csv")
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "category", "segment", "metric", "value", "unit", "direction", "source"])
        
        for m in metrics:
            m.calculate()
            for i, period in enumerate(MONTHS):
                val = round(m.values[i], 2)
                writer.writerow([period, category, "Global", m.name, val, m.unit, m.direction, source])

# FINANCE
finance_metrics = [
    MetricSeries("Revenue (USD)", 7500000, "USD", "up"),
    MetricSeries("Gross Margin (%)", 72.0, "%", "up"),
    MetricSeries("EBITDA Margin (%)", 26.0, "%", "up"),
    MetricSeries("Net Profit Margin (%)", 13.0, "%", "up"),
    MetricSeries("Cash Runway (Months)", 18.0, "Months", "up"),
    MetricSeries("Debt to Equity Ratio", 0.85, "Ratio", "down"),
    MetricSeries("CAPEX (USD)", 750000, "USD", "down"),
    MetricSeries("OPEX (USD)", 2100000, "USD", "down"),
    MetricSeries("Operating Cash Flow (USD)", 975000, "USD", "up"),
    MetricSeries("Current Ratio", 2.1, "Ratio", "up")
]

# Set Finance targets
finance_metrics[0].set_target("COVID", 0.72)
finance_metrics[1].set_target("COVID", 0.91)
finance_metrics[2].set_target("COVID", 0.55)
finance_metrics[3].set_target("COVID", 0.35)
finance_metrics[4].set_target("COVID", 0.78)

finance_metrics[0].set_target("Recovery", 0.95)
finance_metrics[1].set_target("Recovery", 0.94)
finance_metrics[2].set_target("Recovery", 0.82)

finance_metrics[0].set_target("Churn crisis", 0.91) # Handled dynamically in calculate()
finance_metrics[1].set_target("Churn crisis", 0.96)
finance_metrics[4].set_target("Churn crisis", 0.80)

finance_metrics[7].set_target("Talent crisis", 1.18)
finance_metrics[3].set_target("Talent crisis", 0.78)

finance_metrics[0].set_target("Cyber breach", 0.88)
finance_metrics[7].set_target("Cyber breach", 1.25)

finance_metrics[1].set_target("Ops meltdown", 0.82)
finance_metrics[7].set_target("Ops meltdown", 1.15)


# GROWTH
growth_metrics = [
    MetricSeries("MRR (USD)", 7500000, "USD", "up"),
    MetricSeries("ARR (USD)", 90000000, "USD", "up"),
    MetricSeries("Net Revenue Retention (%)", 112.0, "%", "up"),
    MetricSeries("Monthly Churn Rate (%)", 1.2, "%", "down"),
    MetricSeries("LTV to CAC Ratio", 4.2, "Ratio", "up"),
    MetricSeries("CAC Payback Period (Months)", 11.0, "Months", "down"),
    MetricSeries("New Customers Added (Count)", 85, "Count", "up"),
    MetricSeries("Logo Churn Count (Count)", 8, "Count", "down"),
    MetricSeries("NPS Score", 42, "Score", "up"),
    MetricSeries("CSAT Score (%)", 88.0, "%", "up")
]

growth_metrics[3].set_target("Churn crisis", 4.5)
growth_metrics[2].set_target_absolute("Churn crisis", 87.0)
growth_metrics[4].set_target_absolute("Churn crisis", 1.1)
growth_metrics[5].set_target("Churn crisis", 2.5)

# PEOPLE
people_metrics = [
    MetricSeries("Total Headcount (Count)", 320, "Count", "up"),
    MetricSeries("Annual Turnover Rate (%)", 8.5, "%", "down"),
    MetricSeries("Time to Hire (Days)", 32, "Days", "down"),
    MetricSeries("Employee NPS", 38, "Score", "up"),
    MetricSeries("Revenue per Employee (USD)", 281250, "USD", "up"),
    MetricSeries("Offer Acceptance Rate (%)", 87.0, "%", "up"),
    MetricSeries("Open Positions (Count)", 22, "Count", "down"),
    MetricSeries("Training Hours per Employee (Hours)", 2.3, "Hours", "up"),
    MetricSeries("Engagement Score (%)", 76.0, "%", "up")
]

people_metrics[1].set_target("Talent crisis", 3.2)
people_metrics[2].set_target("Talent crisis", 2.1)
people_metrics[3].set_target_absolute("Talent crisis", -18)
people_metrics[8].set_target("Talent crisis", 0.62)

# OPERATIONS
ops_metrics = [
    MetricSeries("OEE (%)", 84.5, "%", "up"),
    MetricSeries("Defect Rate (%)", 1.1, "%", "down"),
    MetricSeries("First Pass Yield (%)", 93.2, "%", "up"),
    MetricSeries("MTBF (Hours)", 1420, "Hours", "up"),
    MetricSeries("Cycle Time Efficiency (%)", 94.1, "%", "up"),
    MetricSeries("Scrap Rate (%)", 2.3, "%", "down"),
    MetricSeries("Production Output (Units)", 12400, "Units", "up"),
    MetricSeries("Safety Incident Rate (per 200k hours)", 1.4, "Rate", "down")
]

ops_metrics[0].set_target("COVID", 0.8) # arbitrary drop mentioned in prompt
ops_metrics[0].set_target("Ops meltdown", 0.68)
ops_metrics[1].set_target("Ops meltdown", 4.5)
ops_metrics[2].set_target("Ops meltdown", 0.79)
ops_metrics[5].set_target("Ops meltdown", 3.2)

# LOGISTICS
logistics_metrics = [
    MetricSeries("On Time Delivery (%)", 94.2, "%", "up"),
    MetricSeries("Order Fulfillment Cycle Time (Hours)", 36, "Hours", "down"),
    MetricSeries("Inventory Turnover Ratio", 8.4, "Ratio", "up"),
    MetricSeries("Supplier Defect Rate (%)", 0.42, "%", "down"),
    MetricSeries("Carrying Cost of Inventory (%)", 21.0, "%", "down"),
    MetricSeries("Freight Cost per Unit (USD)", 12.80, "USD", "down"),
    MetricSeries("Warehouse Utilization (%)", 78.0, "%", "up")
]

logistics_metrics[0].set_target("COVID", 0.85) # arbitrary disruption
logistics_metrics[0].set_target_absolute("Recovery", 76.0)
logistics_metrics[1].set_target("Recovery", 2.8)
logistics_metrics[2].set_target("Recovery", 0.52)
logistics_metrics[5].set_target("Recovery", 2.1)
logistics_metrics[0].set_target("Ops meltdown", 0.72)
logistics_metrics[1].set_target("Ops meltdown", 1.9)

# IT
it_metrics = [
    MetricSeries("System Uptime (%)", 99.97, "%", "up"),
    MetricSeries("MTTR (Minutes)", 24, "Minutes", "down"),
    MetricSeries("Change Failure Rate (%)", 3.8, "%", "down"),
    MetricSeries("Critical Vulnerabilities (Count)", 0, "Count", "down"),
    MetricSeries("API P99 Latency (ms)", 182, "ms", "down"),
    MetricSeries("Deployment Frequency (per week)", 8.5, "Rate", "up"),
    MetricSeries("Open Incidents (Count)", 3, "Count", "down"),
    MetricSeries("SLA Compliance (%)", 99.3, "%", "up")
]

it_metrics[0].set_target("COVID", 1.0001) # arbitrary boost
it_metrics[0].set_target_absolute("Cyber breach", 92.1)
it_metrics[1].set_target("Cyber breach", 9.0)
it_metrics[3].set_target_absolute("Cyber breach", 12)
it_metrics[6].set_target("Cyber breach", 8.0)
it_metrics[7].set_target_absolute("Cyber breach", 86.0)

# ESG
esg_metrics = [
    MetricSeries("Carbon Footprint tCO2e (metric tons)", 1840, "metric tons", "down"),
    MetricSeries("Renewable Energy Ratio (%)", 52.0, "%", "up"),
    MetricSeries("Board Diversity Ratio (%)", 38.0, "%", "up"),
    MetricSeries("Audit Compliance Score (%)", 97.8, "%", "up"),
    MetricSeries("Privacy Incident Count (Count)", 0, "Count", "down"),
    MetricSeries("Water Usage (m3)", 4200, "m3", "down"),
    MetricSeries("Waste Diverted from Landfill (%)", 68.0, "%", "up")
]

esg_metrics[0].set_target("COVID", 1.45)
esg_metrics[1].set_target_absolute("COVID", 18.0)
esg_metrics[2].set_target_absolute("COVID", 22.0)
esg_metrics[3].set_target_absolute("COVID", 89.0)

# Generate ALL
generate_domain_csv("Finance", finance_metrics, "Finance", "Orange SA Annual Report 2024; FactSet SP500 2024; Bessemer State of Cloud 2024")
generate_domain_csv("Growth", growth_metrics, "Growth", "Bessemer State of Cloud 2024; OpenView SaaS Benchmarks 2024; High Alpha Benchmarks 2024")
generate_domain_csv("People", people_metrics, "People", "SHRM 2024 Workforce Analytics; LinkedIn Talent Insights 2024; Mercer Global Talent Trends 2024")
generate_domain_csv("Operations", ops_metrics, "Operations", "Six Sigma Industry Standards 2024; OSHA Safety Data 2024; ISM Manufacturing PMI 2024")
generate_domain_csv("Logistics", logistics_metrics, "Logistics", "Gartner Supply Chain 2024; ISM Supply Chain Reports 2022-2024; FedEx Logistics Benchmarks 2024")
generate_domain_csv("IT", it_metrics, "IT", "Google DORA Accelerate Report 2024; NIST Cybersecurity Framework 2024; Gartner IT Operations 2024")
generate_domain_csv("ESG", esg_metrics, "ESG", "GRI Global Reporting Initiative 2024; TCFD Framework 2023; CDP Environmental Data 2024")

print("All CSVs generated successfully!")
