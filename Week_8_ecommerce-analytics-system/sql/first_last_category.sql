SELECT
    o.customer_id,

    (
        SELECT p.category
        FROM orders o2
        JOIN order_items oi2
            ON o2.order_id = oi2.order_id
        JOIN products p
            ON oi2.product_id = p.product_id
        WHERE o2.customer_id = o.customer_id
        ORDER BY o2.order_date ASC
        LIMIT 1
    ) AS first_category,

    (
        SELECT p.category
        FROM orders o3
        JOIN order_items oi3
            ON o3.order_id = oi3.order_id
        JOIN products p
            ON oi3.product_id = p.product_id
        WHERE o3.customer_id = o.customer_id
        ORDER BY o3.order_date DESC
        LIMIT 1
    ) AS latest_category

FROM orders o
WHERE o.customer_id IS NOT NULL
GROUP BY o.customer_id;