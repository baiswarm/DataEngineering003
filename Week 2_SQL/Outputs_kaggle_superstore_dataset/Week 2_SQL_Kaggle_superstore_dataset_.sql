  CREATE DATABASE SUPERSTORE;
  USE SUPERSTORE;
  
#1. Load dataset into a SQL database.

#2.Explore table (schema, sample data):
SELECT COUNT(*) AS total_entries
FROM superstore;

SELECT * FROM superstore
LIMIT 10;

#3.Apply WHERE filters (region, category, date, sales).

SELECT * FROM superstore
WHERE Region = 'South';

SELECT * FROM superstore
WHERE sales>=1500;

SELECT * FROM superstore 
WHERE category='Technology';

SELECT *FROM superstore
WHERE 'Order Date' >= '2016-01-01';


#4.Use GROUP BY for aggregations (sales, quantity, averages).

SELECT category,Region ,  SUM(sales) AS total_sales
FROM superstore
GROUP BY category;

SELECT Category,Region,AVG(Profit) AS Avg_Profit
FROM superstore
GROUP BY Category;

SELECT category,Region, SUM(quantity) AS total_quantity
FROM superstore
GROUP BY Region;

# 5.Sort and limit results (top products, top categories).

SELECT `Product Name`,  sales
FROM superstore
LIMIT 20;

SELECT Category,
SUM(Sales) AS total_Sales
FROM superstore
GROUP BY Category
ORDER BY total_Sales DESC
LIMIT 3;

#6.Solve use cases (monthly trends, top customers, duplicates).

SELECT `Customer Name`,sales
FROM superstore
GROUP BY `Customer Name`
ORDER BY sales DESC
LIMIT 10;

SELECT `Order ID`,COUNT(*) AS Total_Count
FROM superstore
GROUP BY `Order ID` HAVING COUNT(*) > 1;

SELECT `Order Date`, SUM(Sales) AS Total_Sales
FROM superstore
GROUP BY `Order Date`
ORDER BY `Order Date`;

# 7.Validate results (row counts, data quality)

SELECT COUNT(*) AS Total_Rows
FROM superstore;

SELECT *
FROM superstore
WHERE Sales IS NULL;

SELECT *
FROM superstore
WHERE category IS NULL;

/* Data quality is good */

#T he Superstore dataset was successfully explored using SQL queries to understand its structure and contents.
# WHERE filters were applied to analyze records based on region, category, sales amount, and order dates.
# GROUP BY operations were used to calculate total sales, profit, and quantity across different categories and regions.
# Sorting and limiting techniques helped identify the top-performing products and categories based on sales.
# Customer analysis revealed the customers contributing the highest sales revenue.
# Duplicate checks showed that some Order IDs appear multiple times because a single order may contain multiple products.
# Data validation queries were performed to verify row counts and check for data quality issues.
