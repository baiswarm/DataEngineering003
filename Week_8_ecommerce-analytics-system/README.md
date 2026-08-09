# 🛒 E-Commerce Order Analytics System

An internship mini-project focused on processing and analyzing e-commerce order data using **Python** and **SQL** — covering the full pipeline from raw data generation to business-ready reports.

---

## 📌 Overview

The E-Commerce Order Analytics System simulates a real-world e-commerce data pipeline. It covers data generation, cleaning, validation, database storage, SQL-based business analysis, and command-line reporting.

---

## 🎯 Objectives

- Generate sample e-commerce data using Python
- Identify and handle data-quality issues
- Clean and validate data using Pandas
- Store cleaned data in a SQLite database
- Perform business analysis using SQL
- Apply advanced SQL concepts such as CTEs and Window Functions
- Generate reports through a command-line interface
- Handle common data edge cases

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Data generation & cleaning |
| Pandas | Data validation & transformation |
| SQL | Business analysis queries |
| SQLite | Data storage |
| Git & GitHub | Version control |

---

## 📂 Datasets

| File | Description |
|------|--------------|
| `orders.csv` | Order details and order status |
| `order_items.csv` | Products, quantities, prices, and discounts per order |
| `products.csv` | Product, category, subcategory, and cost information |
| `customers.csv` | Customer details, registration date, and customer type |

---

## 🧪 Data Generation

Datasets are generated using Python and contain **intentional data-quality issues**, used to demonstrate cleaning and validation:

- Missing customer IDs
- Negative quantities representing returns
- Incorrect date formats
- Inconsistent product names
- Invalid email addresses

---

## 🧹 Data Cleaning

Cleaning is performed using **Pandas** and includes:

- Order date cleaning
- Customer ID validation
- Product name standardization
- Duplicate removal
- Email validation
- Referential integrity checking
- Handling of invalid records

Cleaned datasets are stored separately from the raw datasets.

---

## 🗄️ Database

Cleaned data is loaded into a SQLite database named `ecommerce.db`, containing the following tables:

- `customers`
- `products`
- `orders`
- `order_items`

---

## 📊 SQL Analysis

SQL is used to generate business insights from the cleaned data, including:

- Revenue analysis
- Customer analysis
- Product analysis
- Monthly order analysis
- Running totals
- Product ranking
- Customer order-gap analysis
- CTE-based analysis
- Customer segmentation
- Year-over-Year analysis
- Cohort analysis
- Cumulative revenue analysis
- Frequently bought together products

---

## 💻 Command-Line Reporting

A CLI reporting tool generates reports directly from the SQLite database.

**Example:**

    python report_cli.py --report monthly --start 2024-01-01 --end 2024-12-31

**Report output includes:**

- Total orders
- Total revenue
- Unique customers
- Top 3 products
- Revenue comparison

**Supported report types:** Daily · Weekly · Monthly

---

## ⚠️ Edge Case Handling

The project includes tests for:

- Invalid order IDs
- Discounts greater than 100%
- Zero quantity
- Future order dates

---

## 🔗 Frequently Bought Together

Identifies product pairs frequently purchased together, reporting:

- Product A
- Product B
- Number of times purchased together

Duplicate product pairs are automatically avoided.

---

## 🔄 Project Workflow

Raw Data → Data Generation → Data Cleaning & Validation → Cleaned Data → SQLite Database → SQL Analysis → Command-Line Reports

---

## 📁 Project Structure

    ecommerce-analytics/
    ├── data/
    │   ├── raw/                   # Raw generated datasets
    │   └── cleaned/                # Cleaned datasets
    ├── scripts/
    │   ├── generate_data.py        # Generates the datasets
    │   ├── clean_data.py           # Cleans and validates the data
    │   ├── setup_database.py       # Creates the SQLite database
    │   ├── report_cli.py           # Generates command-line reports
    │   └── test_edge_cases.py      # Runs edge-case tests
    ├── sql/                        # SQL analysis queries
    ├── ecommerce.db                 # SQLite database
    ├── edge_cases.md                # Edge-case documentation
    └── README.md                    # Project documentation

---

## ▶️ How to Run

**1. Generate Data**

    python generate_data.py

**2. Clean Data**

    python clean_data.py

**3. Create SQLite Database**

    python setup_database.py

**4. Run Edge-Case Tests**

    python test_edge_cases.py

**5. Generate a Report**

    python report_cli.py --report monthly --start 2024-01-01 --end 2024-12-31

---

## ✅ Conclusion

This project demonstrates an end-to-end e-commerce data analytics workflow using Python, Pandas, and SQL — covering data generation, cleaning, validation, analysis, testing, and business reporting.
