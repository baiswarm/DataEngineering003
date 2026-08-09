import sqlite3
import argparse

# Connect to SQLite
conn = sqlite3.connect("../ecommerce.db")
cursor = conn.cursor()

# Command line arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    "--report",
    choices=["daily", "weekly", "monthly"],
    required=True
)

parser.add_argument("--start", required=True)
parser.add_argument("--end", required=True)

args = parser.parse_args()

start = args.start
end = args.end

# ---------------- SUMMARY ----------------

cursor.execute("""
SELECT
    COUNT(DISTINCT o.order_id),
    SUM(oi.quantity * oi.unit_price *
        (1 - oi.discount_percent / 100.0)),
    COUNT(DISTINCT o.customer_id)
FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id
WHERE date(o.order_date) BETWEEN date(?) AND date(?)
""", (start, end))

result = cursor.fetchone()

total_orders = result[0] or 0
revenue = result[1] or 0
unique_customers = result[2] or 0

print("\n===== E-COMMERCE REPORT =====")
print("Report Type:", args.report)
print("Date Range:", start, "to", end)

print("\nTotal Orders:", total_orders)
print("Revenue:", round(revenue, 2))
print("Unique Customers:", unique_customers)


# ---------------- TOP 3 PRODUCTS ----------------

cursor.execute("""
SELECT
    p.product_name,
    SUM(oi.quantity) AS quantity_sold
FROM order_items oi
JOIN products p
ON oi.product_id = p.product_id
JOIN orders o
ON oi.order_id = o.order_id
WHERE date(o.order_date) BETWEEN date(?) AND date(?)
GROUP BY p.product_id, p.product_name
ORDER BY quantity_sold DESC
LIMIT 3
""", (start, end))

print("\nTop 3 Products:")

for row in cursor.fetchall():
    print(row[0], "-", row[1], "units")


# ---------------- PREVIOUS PERIOD ----------------

cursor.execute("""
SELECT
    SUM(oi.quantity * oi.unit_price *
        (1 - oi.discount_percent / 100.0))
FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id
WHERE date(o.order_date) < date(?)
""", (start,))

previous_revenue = cursor.fetchone()[0] or 0

if previous_revenue != 0:
    change = ((revenue - previous_revenue) / previous_revenue) * 100
else:
    change = 0

print("\nRevenue Change:", round(change, 2), "%")

cursor.close()
conn.close()