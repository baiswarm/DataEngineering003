"""
Validation harness (pandas, NOT PySpark) — proves the corrected SCD2 + Gold
logic is right before it goes into the actual Databricks notebooks.

I don't have a Databricks/Spark cluster or your real tables available here,
so this is a stand-in: same schema, same logic, small synthetic dataset,
so you can see the exact bug vs fix side by side with real numbers.
"""
import pandas as pd

pd.set_option("display.width", 120)

# ---------------------------------------------------------------------
# 1. Synthetic silver_contracts (already deduped, this is what the raw
#    "vendor_contracts" history looks like BEFORE any SCD2 processing)
# ---------------------------------------------------------------------
contracts = pd.DataFrame([
    # vendor_id, item_name,  negotiated_price, valid_from,  payment_terms
    ("V001", "Steel Rod", 100.0, "2025-01-01", "Net30"),
    ("V001", "Steel Rod", 120.0, "2025-04-01", "Net30"),
    ("V001", "Steel Rod", 110.0, "2025-08-01", "Net60"),
    ("V002", "Copper Wire", 50.0, "2025-01-01", "Net30"),
])
contracts.columns = ["vendor_id", "item_name", "negotiated_price", "valid_from", "payment_terms"]
contracts["valid_from"] = pd.to_datetime(contracts["valid_from"])

# ---------------------------------------------------------------------
# 2. CORRECTED SCD2 build (equivalent to the LEAD()-window-function SQL
#    in the fixed 03_SCD_Type2.py) — one deterministic pass over full
#    history, no MERGE-against-itself confusion.
# ---------------------------------------------------------------------
scd2 = contracts.sort_values(["vendor_id", "item_name", "valid_from"]).copy()
scd2["start_date"] = scd2["valid_from"]
scd2["next_valid_from"] = scd2.groupby(["vendor_id", "item_name"])["valid_from"].shift(-1)
scd2["end_date"] = (scd2["next_valid_from"] - pd.Timedelta(days=1))
scd2["is_active"] = scd2["next_valid_from"].isna()
scd2 = scd2.drop(columns=["next_valid_from", "valid_from"])

print("=" * 90)
print("CORRECTED silver_vendor_contracts (SCD2) — one row per contract version,")
print("each with the correct start/end window, only ONE is_active=True per vendor+item")
print("=" * 90)
print(scd2.to_string(index=False))
print()

# sanity check: exactly one active row per vendor+item
active_counts = scd2[scd2.is_active].groupby(["vendor_id", "item_name"]).size()
assert (active_counts == 1).all(), "SCD2 broken: more than one active row per vendor+item"
print("CHECK PASSED: exactly one is_active=True row per vendor_id+item_name\n")

# ---------------------------------------------------------------------
# 3. Synthetic orders + invoices
# ---------------------------------------------------------------------
orders = pd.DataFrame([
    ("PO1", "V001", "Steel Rod", 10, "2025-02-15"),
    ("PO2", "V001", "Steel Rod", 5,  "2025-05-10"),
    ("PO3", "V001", "Steel Rod", 8,  "2025-09-01"),
], columns=["po_id", "vendor_id", "item_name", "quantity_requested", "po_timestamp"])
orders["po_timestamp"] = pd.to_datetime(orders["po_timestamp"])

invoices = pd.DataFrame([
    ("INV1", "PO1", "V001", 105.0, "Paid"),
    ("INV2", "PO2", "V001", 120.0, "Paid"),
    ("INV3", "PO3", "V001", 108.0, "Overdue"),
], columns=["invoice_id", "po_id", "vendor_id", "invoiced_price_per_unit", "payment_status"])

# ---------------------------------------------------------------------
# 4a. ORIGINAL (buggy) gold_price_variance_report logic:
#     join on vendor_id only, filter WHERE c.is_active = true
#     -> ALWAYS compares against the CURRENT contract, regardless of
#        when the PO actually happened
# ---------------------------------------------------------------------
current_contract = scd2[scd2.is_active][["vendor_id", "item_name", "negotiated_price"]]
buggy = orders.merge(invoices, on=["po_id", "vendor_id"]).merge(
    current_contract, on="vendor_id"  # <-- bug: not joined on item_name either
)
buggy["price_difference"] = buggy["invoiced_price_per_unit"] - buggy["negotiated_price"]
buggy["charge_status"] = buggy["price_difference"].apply(lambda x: "Overcharged" if x > 0 else "OK")

print("=" * 90)
print("BEFORE FIX — gold_price_variance_report (always uses the CURRENT active")
print("contract, i.e. the Aug 2025 price of 110, no matter when the PO happened)")
print("=" * 90)
print(buggy[["po_id", "invoiced_price_per_unit", "negotiated_price", "price_difference", "charge_status"]]
      .to_string(index=False))
print()

# ---------------------------------------------------------------------
# 4b. CORRECTED gold_price_variance_report logic:
#     join on vendor_id AND item_name, match the PO date INSIDE the
#     contract's [start_date, end_date] window (open-ended if end_date
#     is null) -> uses the contract that was actually active at the
#     time of that specific purchase
# ---------------------------------------------------------------------
merged = orders.merge(invoices, on=["po_id", "vendor_id"]).merge(
    scd2, on=["vendor_id", "item_name"]
)
in_window = (
    (merged["po_timestamp"] >= merged["start_date"]) &
    (merged["end_date"].isna() | (merged["po_timestamp"] <= merged["end_date"]))
)
fixed = merged[in_window].copy()
fixed["price_difference"] = fixed["invoiced_price_per_unit"] - fixed["negotiated_price"]
fixed["charge_status"] = fixed["price_difference"].apply(lambda x: "Overcharged" if x > 0 else "OK")

print("=" * 90)
print("AFTER FIX — gold_price_variance_report (uses the contract version that")
print("was actually active on each PO's own po_timestamp)")
print("=" * 90)
print(fixed[["po_id", "po_timestamp", "invoiced_price_per_unit", "negotiated_price",
             "price_difference", "charge_status"]].to_string(index=False))
print()

print("=" * 90)
print("WHY THIS MATTERS")
print("=" * 90)
print("PO2 (May 2025): buggy report says +10 overcharge (compares $120 invoice vs")
print("today's $110 contract). Correct report says $0 variance, because in May the")
print("active contract price WAS $120 — the invoice matched the contract exactly.")
print("PO1 (Feb 2025): buggy report says -5 (looks fine). Correct report says +5")
print("overcharged, because the Jan contract price was $100, not $110.")
print("This is exactly the business question the blueprint asks the project to")
print("answer, so this join is the most important fix in the whole pipeline.")
print()

# ---------------------------------------------------------------------
# 5. CORRECTED risk classification (percentage variance + overdue flag,
#    matching the blueprint's rule exactly)
# ---------------------------------------------------------------------
vendor_overdue = invoices.groupby("vendor_id")["payment_status"].apply(
    lambda s: (s == "Overdue").any()
).rename("has_overdue")

risk_input = fixed.copy()
risk_input["pct_variance"] = (risk_input["price_difference"] / risk_input["negotiated_price"]) * 100
risk = risk_input.groupby("vendor_id")["pct_variance"].mean().to_frame("avg_pct_variance")
risk = risk.join(vendor_overdue)

def classify(row):
    if row.avg_pct_variance > 10 and row.has_overdue:
        return "High Risk"
    elif row.avg_pct_variance > 5 or row.has_overdue:
        return "Medium Risk"
    return "Low Risk"

risk["risk"] = risk.apply(classify, axis=1)
print("=" * 90)
print("AFTER FIX — gold_vendor_risk_classification (% variance + overdue flag,")
print("matches the blueprint rule instead of a made-up flat dollar threshold)")
print("=" * 90)
print(risk.to_string())
