import pandas as pd
import random
import os
from datetime import datetime, timedelta

os.makedirs("../data/raw", exist_ok=True)

random.seed(42)

# ---------------- CUSTOMERS ----------------

customers = []

for i in range(1, 501):
    customers.append({
        "customer_id": i,
        "customer_name": f"Customer {i}",
        "email": f"customer{i}@example.com",
        "registration_date": (
            datetime(2024, 1, 1) +
            timedelta(days=random.randint(0, 700))
        ).strftime("%Y-%m-%d"),
        "customer_type": random.choice(
            ["REGULAR", "PREMIUM", "VIP"]
        )
    })

customers_df = pd.DataFrame(customers)

# 2% invalid emails
for i in random.sample(range(500), 10):
    customers_df.loc[i, "email"] = f"invalid_email_{i}"

# ---------------- PRODUCTS ----------------

categories = ["Electronics", "Clothing", "Home", "Books"]

products = []

for i in range(1, 501):
    products.append({
        "product_id": i,
        "product_name": f"Product {i}",
        "category": random.choice(categories),
        "subcategory": f"Subcategory {(i % 10) + 1}",
        "cost_price": round(random.uniform(50, 2000), 2)
    })

products_df = pd.DataFrame(products)

# Messy product names
products_df.loc[5, "product_name"] = "  laptop "
products_df.loc[10, "product_name"] = "SMART PHONE"
products_df.loc[20, "product_name"] = "  headphones"

# ---------------- ORDERS ----------------

orders = []

statuses = [
    "PLACED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "RETURNED"
]

for i in range(1, 1001):
    customer_id = random.randint(1, 500)

    orders.append({
        "order_id": i,
        "customer_id": customer_id,
        "order_date": (
            datetime(2024, 1, 1) +
            timedelta(days=random.randint(0, 700),
                      hours=random.randint(0, 23))
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "status": random.choice(statuses),
        "region_code": random.choice(
            ["NORTH", "SOUTH", "EAST", "WEST"]
        )
    })

orders_df = pd.DataFrame(orders)

# 5% NULL customer IDs
for i in random.sample(range(1000), 50):
    orders_df.loc[i, "customer_id"] = None

# Some wrong date formats
for i in random.sample(range(1000), 20):
    date = datetime(2024, 1, 1) + timedelta(
        days=random.randint(0, 700)
    )
    orders_df.loc[i, "order_date"] = date.strftime("%d-%m-%Y")

# ---------------- ORDER ITEMS ----------------

order_items = []

item_id = 1

for order_id in range(1, 1001):

    number_of_items = random.randint(1, 3)

    for _ in range(number_of_items):

        product_id = random.randint(1, 500)
        quantity = random.randint(1, 5)

        order_items.append({
            "item_id": item_id,
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": round(
                random.uniform(100, 5000), 2
            ),
            "discount_percent": round(
                random.uniform(0, 30), 2
            )
        })

        item_id += 1

order_items_df = pd.DataFrame(order_items)

# 3% negative quantities = returns
negative_rows = random.sample(
    range(len(order_items_df)),
    int(len(order_items_df) * 0.03)
)

for i in negative_rows:
    order_items_df.loc[i, "quantity"] *= -1

# ---------------- SAVE ----------------

customers_df.to_csv(
    "../data/raw/customers.csv",
    index=False
)

products_df.to_csv(
    "../data/raw/products.csv",
    index=False
)

orders_df.to_csv(
    "../data/raw/orders.csv",
    index=False
)

order_items_df.to_csv(
    "../data/raw/order_items.csv",
    index=False
)

print("Data generation completed!")
print("Customers:", len(customers_df))
print("Products:", len(products_df))
print("Orders:", len(orders_df))
print("Order Items:", len(order_items_df))