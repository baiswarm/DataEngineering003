import pandas as pd
import os

os.makedirs("../data/cleaned", exist_ok=True)

customers = pd.read_csv("../data/raw/customers.csv")
products = pd.read_csv("../data/raw/products.csv")
orders = pd.read_csv("../data/raw/orders.csv")
order_items = pd.read_csv("../data/raw/order_items.csv")


def clean_orders():
    global orders

    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        dayfirst=True,
        errors="coerce"
    )

    orders = orders.dropna(subset=["customer_id"])
    orders["customer_id"] = orders["customer_id"].astype(int)

    return orders


def clean_products():
    global products

    products["product_name"] = (
        products["product_name"]
        .str.strip()
        .str.title()
    )

    return products


def validate_emails():
    invalid = customers[
        ~customers["email"].str.contains(
            "@", na=False
        )
    ]

    return invalid["customer_id"].tolist()


def check_referential_integrity():
    invalid = order_items[
        ~order_items["order_id"].isin(
            orders["order_id"]
        )
    ]

    return invalid


# Clean customers
customers = customers.drop_duplicates()

# Clean orders
orders = clean_orders()
orders = orders.drop_duplicates()

# Clean products
products = clean_products()
products = products.drop_duplicates()

# Validate emails
invalid_emails = validate_emails()

# Referential integrity
invalid_items = check_referential_integrity()

# Remove invalid order items
order_items = order_items[
    order_items["order_id"].isin(orders["order_id"])
]

order_items = order_items[
    order_items["product_id"].isin(products["product_id"])
]

order_items = order_items.drop_duplicates()


# Save cleaned data

customers.to_csv(
    "../data/cleaned/customers_clean.csv",
    index=False
)

products.to_csv(
    "../data/cleaned/products_clean.csv",
    index=False
)

orders.to_csv(
    "../data/cleaned/orders_clean.csv",
    index=False
)

order_items.to_csv(
    "../data/cleaned/order_items_clean.csv",
    index=False
)

# Issue report

with open("../data/cleaned/issue_report.txt", "w") as f:
    f.write(
        f"Invalid emails found: {len(invalid_emails)}\n"
    )
    f.write(
        f"Invalid order items found: {len(invalid_items)}\n"
    )

print("Cleaning completed successfully!")