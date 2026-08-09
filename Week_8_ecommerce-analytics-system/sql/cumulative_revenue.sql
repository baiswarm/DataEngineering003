WITH customer_revenue AS (
    SELECT
        o.customer_id,
        SUM(
            oi.quantity * oi.unit_price *
            (1 - oi.discount_pct / 100.0)
        ) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
)

SELECT
    customer_id,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        SUM(revenue) OVER (ORDER BY revenue DESC),
        2
    ) AS cumulative_revenue,
    ROUND(
        100.0 * SUM(revenue) OVER (ORDER BY revenue DESC)
        / SUM(revenue) OVER (),
        2
    ) AS cumulative_percent
FROM customer_revenue
ORDER BY revenue DESC;