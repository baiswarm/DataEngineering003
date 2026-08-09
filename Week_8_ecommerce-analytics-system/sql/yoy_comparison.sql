WITH monthly_revenue AS (
    SELECT
        STRFTIME('%Y', o.order_date) AS year,
        STRFTIME('%m', o.order_date) AS month,
        SUM(
            oi.quantity * oi.unit_price *
            (1 - oi.discount_percent / 100.0)
        ) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    GROUP BY year, month
)

SELECT
    year,
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        LAG(revenue, 12) OVER (
            ORDER BY year, month
        ),
        2
    ) AS prev_year_revenue
FROM monthly_revenue
ORDER BY year, month;