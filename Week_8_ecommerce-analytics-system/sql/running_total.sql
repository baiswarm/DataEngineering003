WITH daily_revenue AS (
    SELECT
        o.region_code,
        DATE(o.order_date) AS order_date,
        SUM(
            oi.quantity * oi.unit_price *
            (1 - oi.discount_percent / 100.0)
        ) AS daily_revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    GROUP BY o.region_code, DATE(o.order_date)
)

SELECT
    region_code,
    order_date,
    daily_revenue,
    SUM(daily_revenue) OVER (
        PARTITION BY region_code
        ORDER BY order_date
    ) AS running_total
FROM daily_revenue
ORDER BY region_code, order_date;