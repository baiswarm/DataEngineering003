from faker import Faker
import pandas as pd
import random
import os

fake = Faker()

# Create raw folder
os.makedirs("../data/raw", exist_ok=True)

NUM_CUSTOMERS = 100
NUM_PRODUCTS = 50
NUM_ORDERS = 300

# ------------------ CUSTOMERS ------------------

customers = []

for i in range(1, NUM_CUSTOMERS + 1):
    customers.append({
        "customer_id": i,
        "customer_name": fake.name(),
        "email": fake.email(),
        "city": fake.city(),
        "segment": random.choice(["Regular", "Premium", "VIP"])
    })

customers_df = pd.DataFrame(customers)

customers_df.loc[5, "email"] = None
customers_df = pd.concat([customers_df, customers_df.iloc[[0]]], ignore_index=True)

# ------------------ PRODUCTS ------------------

products = []

categories = ["Electronics", "Furniture", "Clothing", "Groceries"]

for i in range(1, NUM_PRODUCTS + 1):
    products.append({
        "product_id": i,
        "product_name": fake.word().title(),
        "category": random.choice(categories),
        "price": round(random.uniform(100, 5000), 2)
    })

products_df = pd.DataFrame(products)

products_df.loc[3, "category"] = None
products_df = pd.concat([products_df, products_df.iloc[[2]]], ignore_index=True)

# ------------------ ORDERS ------------------

orders = []

for i in range(1, NUM_ORDERS + 1):
    orders.append({
        "order_id": i,
        "customer_id": random.randint(1, NUM_CUSTOMERS),
        "order_date": fake.date_between(start_date="-2y", end_date="today"),
        "status": random.choice(["Completed", "Pending", "Cancelled"])
    })

orders_df = pd.DataFrame(orders)

orders_df.loc[10, "customer_id"] = 9999
orders_df.loc[15, "order_date"] = None

# ------------------ ORDER ITEMS ------------------

order_items = []

for i in range(1, NUM_ORDERS + 1):
    order_items.append({
        "order_item_id": i,
        "order_id": random.randint(1, NUM_ORDERS),
        "product_id": random.randint(1, NUM_PRODUCTS),
        "quantity": random.randint(1, 5)
    })

order_items_df = pd.DataFrame(order_items)

order_items_df.loc[20, "product_id"] = 9999
order_items_df = pd.concat([order_items_df, order_items_df.iloc[[5]]], ignore_index=True)

# ------------------ SAVE CSV ------------------

customers_df.to_csv("../data/raw/customers.csv", index=False)
products_df.to_csv("../data/raw/products.csv", index=False)
orders_df.to_csv("../data/raw/orders.csv", index=False)
order_items_df.to_csv("../data/raw/order_items.csv", index=False)

print("All datasets generated successfully!")