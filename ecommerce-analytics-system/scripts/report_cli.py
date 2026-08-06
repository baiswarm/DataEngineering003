import argparse
import mysql.connector

# Database Connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="root",
        database="ecommerce"
    )
except mysql.connector.Error as err:
    print("Database Connection Error:", err)
    exit()

cursor = conn.cursor()

# Read Command Line Argument
parser = argparse.ArgumentParser()
parser.add_argument("--report", required=True)
args = parser.parse_args()

# Revenue Report
if args.report == "revenue":

    cursor.execute("""
    SELECT
        category,
        SUM(price * quantity) AS revenue
    FROM products p
    JOIN order_items oi
    ON p.product_id = oi.product_id
    GROUP BY category;
    """)

    print("\nRevenue Report\n")

    rows = cursor.fetchall()

    if len(rows) == 0:
        print("No data found.")
    else:
        for row in rows:
            print(row)

# Customer Report
elif args.report == "customers":

    cursor.execute("""
    SELECT
        customer_id,
        COUNT(order_id) AS total_orders
    FROM orders
    GROUP BY customer_id;
    """)

    print("\nCustomer Report\n")

    rows = cursor.fetchall()

    if len(rows) == 0:
        print("No data found.")
    else:
        for row in rows:
            print(row)

# Product Report
elif args.report == "products":

    cursor.execute("""
    SELECT
        product_name,
        SUM(quantity) AS quantity_sold
    FROM products p
    JOIN order_items oi
    ON p.product_id = oi.product_id
    GROUP BY product_name
    ORDER BY quantity_sold DESC;
    """)

    print("\nTop Products Report\n")

    rows = cursor.fetchall()

    if len(rows) == 0:
        print("No data found.")
    else:
        for row in rows:
            print(row)

# Invalid Input
else:
    print("Invalid Report")

cursor.close()
conn.close()