# IntelAI Raw Datasets Index

This document tracks all real-world, verifiable datasets (CSV, JSON, GeoJSON, Parquet, Logs, XBRL) downloaded to power IntelAI's multi-domain analytics engine and GraphRAG.

## 1. Finance (`finance/`)
* **XBRL Company Facts**: Microsoft, Apple, and Salesforce (from SEC EDGAR API, JSON format).
* **Corporate Invoices / Ledgers**: Finance_Accounting_General_Ledger.csv.
* **Tickers**: SEC_EDGAR_Company_Tickers_Index.json.

## 2. Growth / SaaS (`growth/`)
* **Churn Analytics**: IBM Telco Customer Churn (CSV).
* **Retail Transactions**: UCI Online Retail Ecommerce dataset (Excel).

## 3. HR / People (`people/`)
* **Workforce Analytics**: HR Employee Dataset, US BLS Employment Earnings Data, HR Analytics Dataset Verified.

## 4. Operations (`operations/`)
* **Predictive Maintenance / SCADA**: AI4I Predictive Maintenance, Hydraulic System Condition Monitoring (CSV).
* **Manufacturing Quality (IoT/Sensor)**: SECOM Semiconductor Manufacturing (IoT + Labels), SoliDAIR manufacturing quality prediction, Steel Plates Faults Quality Inspection.

## 5. Logistics (`logistics/`)
* **Routing / Fleet**: NYC TLC Taxi Trips Jan 2023 (Parquet).
* **Transport / Safety**: UK Road Traffic Transport Logistics (CSV).
* **Mapping**: World Ports Logistics Map (GeoJSON).

## 6. IT / Cybersecurity (`it/`)
* **CI/CD Events**: GitHub Public CI/CD Events Sample (JSON).
* **IT Service Management (ITSM)**: IT HelpDesk Tickets (Excel), IT Support Tickets Classification (CSV).
* **Web Server Logs**: Apache Web Server Access Logs (log format).

## 7. ESG (`esg/`)
* **Emissions & Energy Mix**: OurWorldInData Global CO2 Emissions, OurWorldInData Global Energy Mix (CSV).
* **World Bank Open Data**: CO2 Emissions Per Capita, Electric Power Consumption, Renewable Energy Access (JSON).

## Quality Assurance Note
All data is 100% real, downloaded from primary public sources (SEC EDGAR, World Bank, Kaggle, UCI Machine Learning Repository, Zenodo, UK Government, NYC TLC, GitHub Archive).
