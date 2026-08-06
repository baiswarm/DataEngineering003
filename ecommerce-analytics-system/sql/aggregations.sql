## AGGREGATIONS ##

-- Revenue Per Customer

SELECT
    c.customer_id,
    c.customer_name,
    SUM(p.price * oi.quantity) AS total_revenue
FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
JOIN order_items oi
ON o.order_id = oi.order_id
JOIN products p
ON oi.product_id = p.product_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_revenue DESC;

-- Revenue Per Category

SELECT
    p.category,
    SUM(p.price * oi.quantity) AS revenue
FROM products p
JOIN order_items oi
ON p.product_id = oi.product_id
GROUP BY p.category;


-- Revenue Per Month
SELECT
    DATE_FORMAT(o.order_date, '%Y-%m') AS month,
    SUM(p.price * oi.quantity) AS revenue
FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id
JOIN products p
ON oi.product_id = p.product_id
GROUP BY month
ORDER BY month;



-- Top Products by Revenue
SELECT
    p.product_name,
    SUM(oi.quantity) AS quantity_sold,
    SUM(p.price * oi.quantity) AS revenue
FROM products p
JOIN order_items oi
ON p.product_id = oi.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 10;


-- Average Order Value
SELECT
    AVG(order_total) AS average_order_value
FROM
(SELECT
	o.order_id,
	SUM(p.price * oi.quantity) AS order_total
    FROM orders o
    JOIN order_items oi
    ON o.order_id = oi.order_id
    JOIN products p
    ON oi.product_id = p.product_id
    GROUP BY o.order_id
) t;
