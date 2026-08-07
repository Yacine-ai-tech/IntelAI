#!/usr/bin/env python3
"""
IntelAI ETL Mapper Script for Raw CSV Datasets.

This script demonstrates how to map arbitrary real-world raw datasets 
(like the Kaggle HR datasets or General Ledger exports) into the strict 
`kpi_metrics` time-series schema required by the IntelAI ingestion engine.

Expected IntelAI API Schema:
['period', 'category', 'segment', 'metric', 'value', 'unit', 'direction', 'source']
"""

import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="IntelAI ETL CSV Mapper")
    parser.add_argument("--input", type=str, required=True, help="Path to raw CSV file")
    parser.add_argument("--output", type=str, default="mapped_kpi_dataset.csv", help="Output path")
    parser.add_argument("--category", type=str, default="General", help="Domain category (e.g., Finance, People)")
    parser.add_argument("--metric-col", type=str, required=True, help="Column name to extract as the value")
    parser.add_argument("--date-col", type=str, default=None, help="Column name for dates (to extract YYYY-MM)")
    parser.add_argument("--metric-name", type=str, default="Mapped_Metric", help="The name of the extracted metric")
    return parser.parse_args()

def map_raw_to_kpi(input_path: Path, output_path: Path, category: str, metric_col: str, date_col: str, metric_name: str):
    print(f"📥 Loading raw dataset: {input_path.name}")
    df_raw = pd.read_csv(input_path)
    
    if metric_col not in df_raw.columns:
        raise ValueError(f"Metric column '{metric_col}' not found in {list(df_raw.columns)}")
        
    kpi_records = []
    
    # Process each row in the raw dataset
    for idx, row in df_raw.iterrows():
        # Handle Period (YYYY-MM)
        period = "2026-01" # Default fallback
        if date_col and date_col in df_raw.columns:
            try:
                # Attempt to parse date and format as YYYY-MM
                dt = pd.to_datetime(row[date_col])
                period = dt.strftime("%Y-%m")
            except:
                pass
                
        # Extract the value safely
        try:
            val = float(row[metric_col])
        except (ValueError, TypeError):
            continue # Skip invalid rows
            
        kpi_records.append({
            "period": period,
            "category": category,
            "segment": "Total",
            "metric": metric_name,
            "value": val,
            "unit": "count/raw",
            "direction": "up_is_good", # Default
            "source": input_path.name
        })
        
    df_mapped = pd.DataFrame(kpi_records)
    
    # We must match the expected API headers exactly
    expected_headers = ['period', 'category', 'segment', 'metric', 'value', 'unit', 'direction', 'source']
    df_mapped = df_mapped[expected_headers]
    
    # Aggregate to monthly level if there are multiple records per month
    df_agg = df_mapped.groupby(['period', 'category', 'segment', 'metric', 'unit', 'direction', 'source'], as_index=False)['value'].sum()
    
    df_agg.to_csv(output_path, index=False)
    print(f"✅ Successfully mapped {len(df_agg)} KPI records to {output_path.name}")

if __name__ == "__main__":
    args = parse_args()
    map_raw_to_kpi(
        input_path=Path(args.input),
        output_path=Path(args.output),
        category=args.category,
        metric_col=args.metric_col,
        date_col=args.date_col,
        metric_name=args.metric_name
    )
