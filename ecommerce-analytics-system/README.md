# E-Commerce Analytics System

## Overview

The E-Commerce Analytics System is an end-to-end data analytics project developed using **Python, Pandas, Faker, and MySQL**. The project simulates an e-commerce environment by generating realistic datasets, cleaning and validating data, storing it in a relational database, performing SQL analytics, and generating business reports through a Command Line Interface (CLI).

---

## Objectives

- Generate realistic e-commerce datasets.
- Clean and validate data using Pandas.
- Store cleaned datasets in MySQL.
- Perform SQL analytics to derive business insights.
- Analyze customer behavior using cohort analysis and segmentation.
- Generate reports through a Python CLI.
- Handle common edge cases.

---

## Technologies Used

- Python
- Pandas
- Faker
- MySQL
- MySQL Workbench

---

## Project Workflow

### Step 1 – Data Generation
- Generated Customers, Products, Orders, and Order Items datasets.
- Introduced missing values, duplicate records, and invalid IDs.
- Exported raw CSV files.

### Step 2 – Data Cleaning
- Loaded CSV files using Pandas.
- Removed duplicate records.
- Handled missing values.
- Validated customer and product IDs.
- Exported cleaned CSV files.

### Step 3 – Database Design
- Created MySQL database schema.
- Applied Primary Key and Foreign Key constraints.
- Imported cleaned datasets into MySQL.

### Step 4 – SQL Analytics
Implemented:
- Revenue per Customer
- Revenue per Category
- Revenue per Month
- Top Selling Products
- Average Order Value (AOV)

### Step 5 – Window Functions & CTE
Implemented:
- RANK()
- DENSE_RANK()
- Running Total
- Moving Average
- Common Table Expressions (CTEs)

### Step 6 – Cohort & Retention Analysis
Implemented:
- Customer Cohort Analysis
- Monthly Retention Analysis
- Churn vs Repeat Customer Analysis

### Step 7 – Customer Segmentation
Implemented:
- Purchase Frequency Analysis
- Spend Tier Classification
- Basic RFM Analysis

### Step 8 – CLI Reporting Tool

Example commands:

```bash
python scripts/report_cli.py --report revenue
python scripts/report_cli.py --report customers
python scripts/report_cli.py --report products
```

### Step 9 – Edge Cases
Handled:
- Missing Values
- Duplicate Records
- Invalid Customer IDs
- Invalid Product IDs
- Empty SQL Result Sets
- Invalid CLI Arguments
- Database Connection Errors

---

## Project Structure

```
ecommerce-analytics-system/
│
├── data/
│   ├── raw/
│   └── cleaned/
│
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   └── report_cli.py
│
├── sql/
│   ├── schema.sql
│   ├── aggregations.sql
│   ├── window_functions.sql
│   └── cohort_analysis.sql
│
├── output/
│   └── sample_reports/
│
├── edge_cases.md
├── requirements.txt
└── README.md
```

---

## Features

- Synthetic dataset generation using Faker
- Data cleaning and validation using Pandas
- SQL joins and aggregations
- Window Functions
- Common Table Expressions (CTEs)
- Cohort Analysis
- Customer Segmentation
- Command-Line Reporting Tool
- Error and Edge Case Handling

---

## Sample Outputs

The `output/sample_reports` folder contains screenshots of:

- Revenue per Customer
- Revenue per Category
- Revenue per Month
- Top Products
- Average Order Value
- Window Function Results
- CTE Output
- Cohort Analysis
- Customer Segmentation
- CLI Reports

---

## Conclusion

This project demonstrates a complete end-to-end e-commerce analytics pipeline using Python, Pandas, and MySQL. It covers data generation, data cleaning, SQL analytics, customer insights, reporting, and error handling, providing practical experience in data analytics and business intelligence workflows.
