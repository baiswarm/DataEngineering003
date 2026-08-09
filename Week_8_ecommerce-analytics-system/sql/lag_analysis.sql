WITH customer_orders AS (
    SELECT
        customer_id,
        DATE(order_date) AS order_date,
        LAG(DATE(order_date)) OVER (
            PARTITION BY customer_id
            ORDER BY DATE(order_date)
        ) AS previous_order_date
    FROM orders
    WHERE customer_id IS NOT NULL
)

SELECT
    customer_id,
    order_date,
    previous_order_date,
    ROUND(
        JULIANDAY(order_date) -
        JULIANDAY(previous_order_date)
    ) AS days_gap,
    CASE
        WHEN JULIANDAY(order_date) -
             JULIANDAY(previous_order_date) > 30
        THEN 'At Risk'
        ELSE 'Normal'
    END AS risk_status
FROM customer_orders
WHERE previous_order_date IS NOT NULL
ORDER BY customer_id, order_date;