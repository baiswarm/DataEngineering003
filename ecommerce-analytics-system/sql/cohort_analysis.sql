SELECT
customer_id,
MIN(order_date) AS first_purchase
FROM orders
GROUP BY customer_id;


SELECT
customer_id,
COUNT(order_id) AS total_order
FROM orders
GROUP BY customer_id;


SELECT
customer_id,
COUNT(order_id) AS total_orders,
CASE
WHEN COUNT(order_id)=1
THEN 'Churned'
ELSE 'Repeat Customer'
END AS customer_status
FROM orders
GROUP BY customer_id;


SELECT
customer_id,
COUNT(order_id) AS total_orders,
CASE
WHEN COUNT(order_id)=1 THEN 'One Time'
WHEN COUNT(order_id)<=5 THEN 'Occasional'
ELSE 'Loyal'
END AS customer_type
FROM orders
GROUP BY customer_id;


SELECT
c.customer_id,
SUM(p.price*oi.quantity) AS total_spend,
CASE
WHEN SUM(p.price*oi.quantity) < 5000 THEN 'Low'
WHEN SUM(p.price*oi.quantity) < 15000 THEN 'Medium'
ELSE 'High'
END AS spend_tier
FROM customers c
JOIN orders o
ON c.customer_id=o.customer_id
JOIN order_items oi
ON o.order_id=oi.order_id
JOIN products p
ON oi.product_id=p.product_id
GROUP BY c.customer_id;



SELECT
customer_id,
MAX(order_date) AS last_order,
COUNT(order_id) AS frequenc
FROM orders
GROUP BY customer_id;