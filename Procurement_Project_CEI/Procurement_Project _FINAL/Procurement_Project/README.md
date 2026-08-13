# Procurement & Vendor Spend Analytics Pipeline

## Overview

The Procurement & Vendor Spend Analytics Pipeline is an end-to-end data engineering project built using Databricks, PySpark, Spark SQL, Delta Lake, and Azure technologies.

The project processes procurement data through a Medallion Architecture:

**Bronze → Silver → SCD Type 2 → Gold**

The goal is to create a clean, historically tracked, and analytics-ready platform that helps identify vendor spend, invoice price variances, vendor risks, and regional spending patterns.

---

## Business Problem

Procurement contracts can change over time. Prices, payment terms, and other contract conditions may be updated, making it difficult to determine which contract terms were active when a purchase was made.

The project addresses three major problems:

- **Price Inconsistency** – The same item may be purchased at different prices when contract terms change.
- **Invoice Mismatches** – Vendors may invoice more than the agreed contract price.
- **Lack of Historical Tracking** – Previous contract versions may be lost when contracts are updated.

The project aims to answer:

> What was the organization's spend with a vendor using the contract terms that were active when each purchase was made?

---

## Architecture

```text
Raw Procurement Data
        |
        v
+------------------+
|      BRONZE      |
|   Raw Ingestion   |
+------------------+
        |
        v
+------------------+
|      SILVER      |
| Data Cleaning &   |
|   Validation      |
+------------------+
        |
        v
+------------------+
|    SCD TYPE 2     |
| Contract History  |
+------------------+
        |
        v
+------------------+
|       GOLD        |
| Business Analytics|
+------------------+
        |
        v
 Reporting / Dashboarding
```

---

## Technology Stack

- Python
- PySpark
- Spark SQL
- Delta Lake
- Databricks


---

## Source Data

The project works with procurement datasets including:

- Purchase Orders
- Vendor Contracts
- Vendor Invoices
- Vendor Information

The raw data is ingested into Bronze Delta tables while preserving the original records and adding ingestion metadata.

---

## 1. Bronze Layer

The Bronze layer is responsible for raw data ingestion.



### Bronze Tables

- `bronze_orders`
- `bronze_vendor_contracts`
- `bronze_invoices`
- `bronze_vendors`

The Bronze layer acts as the raw foundation of the pipeline.

---

## 2. Silver Layer

The Silver layer cleans and standardizes the Bronze data.

### Data Cleaning

The project performs operations such as:

- Handling missing values.
- Casting columns to appropriate data types.
- Standardizing date formats.
- Removing duplicate records.
- Cleaning and standardizing data values.
- Validating important fields.
- Preparing data for downstream analytics.

### Silver Tables

- `silver_orders`
- `silver_vendor_contracts`
- `silver_invoices`
- `silver_vendors`

The Silver layer provides clean and reliable datasets for further processing.

---

## 3. SCD Type 2

Slowly Changing Dimension Type 2 is implemented on the vendor contract data.

The purpose is to preserve historical contract versions when contract terms change.

### Important Fields

- `vendor_id`
- `item_name`
- `negotiated_price`
- `valid_from`
- `valid_to` / `end_date`
- `is_active`

When a contract changes, the previous version is retained and marked inactive while the new version becomes active.

```text
Previous Contract Version
          |
          v
   is_active = false
          |
          v
     New Version
          |
          v
   is_active = true
```

This allows historical contract information to remain available instead of being overwritten.

---

## 4. Gold Layer

The Gold layer contains business-ready analytical tables created using Spark SQL.

### Vendor Spend Summary

Provides vendor-level spending information including:

- Total spend
- Average invoice amount
- Total orders

**Table:** `gold_vendor_spend_summary`

### Price Variance Report

Compares invoice prices with negotiated contract prices.

The report includes:

- Vendor ID
- Purchase Order ID
- Negotiated price
- Invoice price
- Price difference
- Charge status
- Average vendor variance

**Table:** `gold_price_variance_report`

### Vendor Risk Classification

The project categorizes vendors based on procurement risk indicators.

Risk categories include:

- High Risk
- Medium Risk
- Low Risk

**Table:** `gold_vendor_risk_classification`

### Regional Spend Analysis

Provides spending information by region and vendor.

The analysis helps understand:

- Total spend by region
- Vendor contribution within each region
- Regional procurement patterns

**Table:** `gold_regional_spend_analysis`

---

## 5. Data Quality

Data quality checks are performed throughout the pipeline.

Examples include:

- Null value checks
- Duplicate checks
- Data type validation
- Date validation
- Referential integrity checks
- Contract consistency checks

A separate Data Quality Summary documents the validation results.

---

## 6. Project Structure

```text
Procurement_Project/
│
├── 01_Bronze_Ingestion/
│   └── Bronze notebook
│
├── 02_Silver_Cleansing/
│   └── Silver notebook
│
├── 03_SCD_Type2/
│   └── SCD Type 2 notebook
│
├── 04_Gold_Layer/
│   └── Gold analytics notebook
│
├── Data_Quality_Summary/
│   └── Data Quality Summary
│
├── Final_Presentation/
│   └── Final Presentation.pptx
│
└── README.md
```

---

## 7. Pipeline Workflow

```text
Raw Procurement Data
        |
        v
Bronze Ingestion
        |
        v
Data Cleaning & Validation
        |
        v
Silver Layer
        |
        v
SCD Type 2 Contract History
        |
        v
Gold Business Analytics
        |
        +----------------------+
        |          |           |
        v          v           v
     Vendor      Price       Vendor
     Spend      Variance      Risk
        |
        v
Regional Spend Analysis
        |
        v
Reporting / Dashboarding
```

---

## 8. Key Outcomes

The project demonstrates an end-to-end data engineering workflow covering:

- Data ingestion
- Data cleaning
- Data validation
- Delta Lake storage
- SCD Type 2 implementation
- SQL-based analytics
- Vendor spend analysis
- Price variance analysis
- Risk classification
- Regional spend analysis
- Business reporting

---



## Conclusion

The Procurement & Vendor Spend Analytics Pipeline provides a structured approach to transforming raw procurement data into clean, historically tracked, and business-ready analytical information.

The Medallion Architecture combined with SCD Type 2 enables the organization to preserve contract history while generating useful insights into vendor spending, invoice variances, vendor risk, and regional procurement performance.
