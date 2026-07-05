CREATE DATABASE superstore_sales_db;
USE superstore_sales_db;

SELECT COUNT(*)
FROM superstore_raw;

CREATE TABLE customers (
    customer_id VARCHAR(30),
    customer_name VARCHAR(100)
);

INSERT INTO customers
SELECT DISTINCT `Customer ID`,`Customer Name`
FROM superstore_raw;

CREATE TABLE products (
    product_id VARCHAR(30),
    product_name VARCHAR(255),
    category VARCHAR(100)
);

INSERT INTO products
SELECT DISTINCT
       `Product ID`,
       `Product Name`,
       Category
FROM superstore_raw;

CREATE TABLE orders (
    order_id VARCHAR(30),
    customer_id VARCHAR(30),
    order_date VARCHAR(20),
    sales DOUBLE
);

INSERT INTO orders
SELECT DISTINCT `Order ID`,`Customer ID`,`Order Date`,Sales
FROM superstore_raw;

-- 1.	Find all orders where sales are greater than the average sales. (Subquery) 

SELECT`Order ID`,`Customer Name`,Sales
FROM superstore_raw
WHERE Sales >
(SELECT AVG(Sales) FROM superstore_raw);

-- 2.	Find the highest sales order for each customer. (Subquery) 

SELECT s.`Customer Name`,s.`Order ID`,s.Sales
FROM superstore_raw s
JOIN
(SELECT `Customer Name`,MAX(Sales) AS Highest_Sales
    FROM superstore_raw
    GROUP BY `Customer Name`) m
ON 
s.`Customer Name` = m.`Customer Name`
AND s.Sales = m.Highest_Sales;


-- 3.	Calculate total sales for each customer. (CTE) 

WITH 
customer_sales AS
(SELECT `Customer Name`,SUM(Sales) AS Total_Sales
FROM superstore_raw
GROUP BY `Customer Name`)
SELECT *FROM customer_sales;

-- 4.	Find customers whose total sales are above average. (CTE + Subquery) 
WITH 
customer_sales AS
(SELECT `Customer Name`,SUM(Sales) AS Customer_Sales
    FROM superstore_raw
    GROUP BY `Customer Name`)
SELECT `Customer Name`,Customer_Sales
FROM customer_sales
WHERE Customer_Sales >(SELECT AVG(Customer_Sales)
  FROM customer_sales);
  
  
  -- 5.	Rank all customers based on total sales. (Window Function) 
  
  SELECT `Customer Name`,SUM(Sales) AS Total_Sales,
RANK() OVER (ORDER BY SUM(Sales) DESC) AS rnk
FROM superstore_raw
GROUP BY `Customer Name`;

-- 6.	Assign row numbers to each order within a customer. (Window Function + PARTITION BY) 

SELECT`Customer Name`,`Order ID`,Sales,
ROW_NUMBER() OVER(PARTITION BY `Customer Name` ORDER BY `Order ID`) AS Order_Row_Number
FROM superstore_raw;

-- 7.	Display top 3 customers based on total sales. (Window Function)

SELECT * FROM
(SELECT `Customer Name`, SUM(Sales) AS Total_Sales,
	RANK() OVER (ORDER BY SUM(Sales) DESC) AS Sales_Rank 
    FROM superstore_raw
    GROUP BY `Customer Name`) 
    ranked_customers
WHERE Sales_Rank <= 3;

# ONE FINAL QUERY:

WITH 
customer_sales AS
(SELECT c.customer_name, SUM(o.sales) AS Total_Sales
    FROM customers c
    JOIN orders o
	ON c.customer_id = o.customer_id
    GROUP BY c.customer_name)
SELECT customer_name, Total_Sales,
    RANK() OVER (ORDER BY Total_Sales DESC) AS s_rnk FROM customer_sales;
    
    
    #MINI PROJECT QUESTIONS:
    
  --   1.	Who are the top 5 customers? 
  
 SELECT * FROM
(SELECT `Customer Name`, SUM(Sales) AS Total_Sales,
RANK() OVER (ORDER BY SUM(Sales) DESC) AS Sales_Rank
FROM superstore_raw
GROUP BY `Customer Name`) top_5_customers
WHERE Sales_Rank <= 5;
   
-- 2.	Who are the bottom 5 customers? 
   
SELECT * FROM
(SELECT `Customer Name`,SUM(Sales) AS Total_Sales,
	RANK() OVER (ORDER BY SUM(Sales) ASC) AS Sales_Rank
    FROM superstore_raw
    GROUP BY `Customer Name`) ranked_customers
WHERE Sales_Rank <= 5;


-- 3.	Which customers made only one order? 

SELECT `Customer Name` , COUNT(`Order ID`) AS  Order_Count
FROM superstore_raw
GROUP BY `Customer Name`
HAVING COUNT(`Order ID`) =1;


-- 4.	Which customers have above-average sales? 

WITH customer_sales AS
(SELECT `Customer Name`, SUM(Sales) AS Customer_Sales
FROM superstore_raw
GROUP BY `Customer Name`)

SELECT `Customer Name`, Customer_Sales
FROM customer_sales
WHERE Customer_Sales > (SELECT AVG(Customer_Sales) FROM customer_sales);


-- 5.	What is the highest order value per customer?

SELECT `Customer Name`, MAX(Sales) AS Highest_Order_Value
FROM superstore_raw
GROUP BY `Customer Name`;


    