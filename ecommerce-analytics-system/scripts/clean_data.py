import pandas as pd
import os

os.makedirs("../data/cleaned", exist_ok=True)

# Load datasets
customers = pd.read_csv("../data/raw/customers.csv")
products = pd.read_csv("../data/raw/products.csv")
orders = pd.read_csv("../data/raw/orders.csv")
order_items = pd.read_csv("../data/raw/order_items.csv")

# ---------------- Customers ----------------
customers.drop_duplicates(inplace=True)
customers["email"].fillna("unknown@gmail.com", inplace=True)

# ---------------- Products ----------------
products.drop_duplicates(inplace=True)
products["category"].fillna("Others", inplace=True)

# ---------------- Orders ----------------
orders.drop_duplicates(inplace=True)
orders.dropna(subset=["order_date"], inplace=True)
orders = orders[orders["customer_id"].isin(customers["customer_id"])]

# ---------------- Order Items ----------------
order_items.drop_duplicates(inplace=True)
order_items = order_items[
    order_items["product_id"].isin(products["product_id"])
]

# Save cleaned datasets
customers.to_csv("../data/cleaned/customers_clean.csv", index=False)
products.to_csv("../data/cleaned/products_clean.csv", index=False)
orders.to_csv("../data/cleaned/orders_clean.csv", index=False)
order_items.to_csv("../data/cleaned/order_items_clean.csv", index=False)

print("Cleaning Completed Successfully!")