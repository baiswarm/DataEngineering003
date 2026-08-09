SELECT
c.customer_id,
c.customer_name,
SUM(p.price * oi.quantity) AS total_spend,
RANK() OVER(
ORDER BY SUM(p.price * oi.quantity) DESC
) AS ranking FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
JOIN order_items oi
ON o.order_id = oi.order_id
JOIN products p
ON oi.product_id = p.product_id
GROUP BY
c.customer_id,
c.customer_name;

SELECT
c.customer_id,
c.customer_name,
SUM(p.price * oi.quantity) AS total_spend,
DENSE_RANK() OVER(
ORDER BY SUM(p.price * oi.quantity) DESC
) AS ranking FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
JOIN order_items oi
ON o.order_id = oi.order_id
JOIN products p
ON oi.product_id = p.product_id
GROUP BY
c.customer_id,
c.customer_name;

SELECT
order_date,
SUM(price * quantity) AS total_sales
FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id
JOIN products p
ON oi.product_id = p.product_id
GROUP BY order_date
ORDER BY order_date;


WITH sales AS
(
SELECT
category,
SUM(price*quantity)
AS revenue
FROM products p
JOIN order_items oi
ON p.product_id=oi.product_id
GROUP BY category
)
SELECT *
FROM sales;