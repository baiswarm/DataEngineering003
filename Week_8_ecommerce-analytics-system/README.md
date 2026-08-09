E-Commerce Order Analytics System
Overview

The E-Commerce Order Analytics System is an internship mini project focused on processing and analyzing e-commerce order data using Python and SQL.

The project covers data generation, data cleaning, validation, database storage, SQL analysis, and command-line reporting.

Objectives
Generate sample e-commerce data using Python.
Identify and handle data-quality issues.
Clean and validate data using Pandas.
Store cleaned data in a SQLite database.
Perform business analysis using SQL.
Apply advanced SQL concepts such as CTEs and Window Functions.
Generate reports through a command-line interface.
Handle common data edge cases.
Technologies Used
Python
Pandas
SQL
SQLite
Git & GitHub
Datasets




The project uses four datasets:

orders.csv – Order details and order status.
order_items.csv – Products, quantities, prices, and discounts for each order.
products.csv – Product, category, subcategory, and cost information.
customers.csv – Customer details, registration date, and customer type.
Data Generation

The datasets are generated using Python and contain intentional data-quality issues such as:

Missing customer IDs
Negative quantities representing returns
Incorrect date formats
Inconsistent product names
Invalid email addresses

These issues are used to demonstrate the data cleaning and validation process.

Data Cleaning

The data is cleaned using Pandas.

The project includes:

Order date cleaning
Customer ID validation
Product name standardization
Duplicate removal
Email validation
Referential integrity checking
Handling invalid records

The cleaned datasets are stored separately from the raw datasets.

Database

The cleaned datasets are loaded into a SQLite database named ecommerce.db.

The database contains:

customers
products
orders
order_items
SQL Analysis

SQL is used to generate business insights from the cleaned data.

The analysis includes:

Revenue analysis
Customer analysis
Product analysis
Monthly order analysis
Running totals
Product ranking
Customer order-gap analysis
CTE-based analysis
Customer segmentation
Year-over-Year analysis
Cohort analysis
Cumulative revenue analysis
Frequently bought together products
Command-Line Reporting

A command-line reporting tool is provided to generate reports from the SQLite database.

Example command:

python report_cli.py --report monthly --start 2024-01-01 --end 2024-12-31

The report provides:

Total orders
Total revenue
Unique customers
Top 3 products
Revenue comparison

Supported report types:

Daily
Weekly
Monthly
Edge Case Handling

The project includes tests for:

Invalid order IDs
Discounts greater than 100%
Zero quantity
Future order dates
Frequently Bought Together

The project identifies products that are frequently purchased together.

The analysis provides:

Product A
Product B
Number of times purchased together

Duplicate product pairs are avoided.

Project Workflow

Raw Data → Data Generation → Data Cleaning & Validation → Cleaned Data → SQLite Database → SQL Analysis → Command-Line Reports

Project Structure
data/raw/ – Raw generated datasets
data/cleaned/ – Cleaned datasets
scripts/generate_data.py – Generates the datasets
scripts/clean_data.py – Cleans and validates the data
scripts/setup_database.py – Creates the SQLite database
scripts/report_cli.py – Generates command-line reports
scripts/test_edge_cases.py – Runs edge-case tests
sql/ – SQL analysis queries
ecommerce.db – SQLite database
edge_cases.md – Edge-case documentation
README.md – Project documentation


How to Run
Generate Data

python generate_data.py

Clean Data

python clean_data.py

Create SQLite Database

python setup_database.py

Run Edge-Case Tests

python test_edge_cases.py

Generate a Report

python report_cli.py --report monthly --start 2024-01-01 --end 2024-12-31

Conclusion

This project demonstrates an end-to-end e-commerce data analytics workflow using Python, Pandas, SQL, and SQLite, covering data generation, cleaning, validation, analysis, testing, and business reporting.