# Databricks notebook source
# FIX LOG (see CHANGELOG_FIXES.md):
#   - na.drop() with no subset was dropping a row if ANY column was null,
#     including non-critical ones. Now drops only on the critical key
#     columns the blueprint calls out (vendor_id, po_id/contract_id/
#     invoice_id, price/amount columns), matching "handle nulls in
#     critical columns" instead of silently deleting rows that had a
#     harmless null somewhere unrelated.
#   - Price/amount columns were left as strings and only TRY_CAST'ed
#     later, inside the Gold layer. The blueprint says type casting is a
#     Silver-layer responsibility ("Cast data types: ... amounts to
#     DOUBLE") — casting now happens here, once, so every downstream
#     table already has clean typed columns.
#   - region was never uppercased anywhere, even though the blueprint
#     explicitly calls this out ("convert region to uppercase"). Added
#     to silver_vendors, since region lives on the vendor record in this
#     schema, not on the order.
#   - Added before/after row counts so the Data Quality Summary can cite
#     real numbers (nulls dropped, duplicates removed) instead of
#     descriptive text with no figures behind it.

from pyspark.sql.functions import *
from pyspark.sql.types import DoubleType, IntegerType

bronze_orders = spark.table("workspace.default.bronze_orders")
bronze_contracts = spark.table("workspace.default.bronze_contracts")
bronze_invoices = spark.table("workspace.default.bronze_invoices")
bronze_vendors = spark.table("workspace.default.bronze_vendors")

# COMMAND ----------

# ============================== ORDERS ==============================
raw_count = bronze_orders.count()

silver_orders = bronze_orders.dropDuplicates(["po_id"])
dedup_count = silver_orders.count()

# FIXED: critical-column-only null handling instead of blanket na.drop()
silver_orders = silver_orders.na.drop(subset=["po_id", "vendor_id", "item_name"])
clean_count = silver_orders.count()

silver_orders = silver_orders.withColumn(
    "po_timestamp",
    when(col("po_timestamp") == "N/A - Unknown Date", None)
    .otherwise(col("po_timestamp"))
)

# FIXED: proper DATE type per blueprint (was to_timestamp -> TIMESTAMP)
silver_orders = silver_orders.withColumn("po_timestamp", to_date(col("po_timestamp")))

silver_orders = silver_orders.withColumn("item_name", trim(col("item_name")))

# FIXED: explicit numeric cast in Silver, not deferred to Gold via TRY_CAST
silver_orders = silver_orders.withColumn(
    "quantity_requested", col("quantity_requested").cast(IntegerType())
)

print(f"[DQ] orders: raw={raw_count}  after_dedup={dedup_count}  "
      f"duplicates_removed={raw_count - dedup_count}  "
      f"after_null_drop={clean_count}  nulls_dropped={dedup_count - clean_count}")

silver_orders.show(5)
silver_orders.printSchema()

# COMMAND ----------

silver_orders.write.mode("overwrite").saveAsTable("workspace.default.silver_orders")

# COMMAND ----------

# ============================= CONTRACTS =============================
raw_count = bronze_contracts.count()

silver_contracts = bronze_contracts.dropDuplicates(["contract_id"])
dedup_count = silver_contracts.count()

silver_contracts = silver_contracts.na.drop(
    subset=["vendor_id", "item_name", "negotiated_price", "valid_from"]
)
clean_count = silver_contracts.count()

silver_contracts = silver_contracts.withColumn("item_name", trim(col("item_name")))

silver_contracts = silver_contracts.withColumn(
    "valid_from", expr("try_to_timestamp(valid_from)")
)
# FIXED: proper DATE type (was left as TIMESTAMP from try_to_timestamp)
silver_contracts = silver_contracts.withColumn("valid_from", to_date(col("valid_from")))

# FIXED: explicit numeric cast in Silver
silver_contracts = silver_contracts.withColumn(
    "negotiated_price", col("negotiated_price").cast(DoubleType())
)

# If your raw contracts data has a payment_terms column (Net30/Net60 per
# the blueprint schema), standardize it here so SCD2 change-detection can
# use it too:
if "payment_terms" in silver_contracts.columns:
    silver_contracts = silver_contracts.withColumn(
        "payment_terms", trim(upper(col("payment_terms")))
    )

print(f"[DQ] contracts: raw={raw_count}  after_dedup={dedup_count}  "
      f"duplicates_removed={raw_count - dedup_count}  "
      f"after_null_drop={clean_count}  nulls_dropped={dedup_count - clean_count}")

silver_contracts.show(5)
silver_contracts.printSchema()

# COMMAND ----------

silver_contracts.write.mode("overwrite").saveAsTable("workspace.default.silver_contracts")

# COMMAND ----------

# ============================== INVOICES ==============================
raw_count = bronze_invoices.count()

silver_invoices = bronze_invoices.dropDuplicates(["invoice_id"])
dedup_count = silver_invoices.count()

silver_invoices = silver_invoices.na.drop(
    subset=["invoice_id", "po_id", "vendor_id", "invoiced_price_per_unit"]
)
clean_count = silver_invoices.count()

silver_invoices = silver_invoices.withColumn(
    "invoice_timestamp", expr("try_to_timestamp(invoice_timestamp)")
)
# FIXED: proper DATE type
silver_invoices = silver_invoices.withColumn("invoice_timestamp", to_date(col("invoice_timestamp")))

# FIXED: explicit numeric cast in Silver (was TRY_CAST repeated 3x in Gold)
silver_invoices = silver_invoices.withColumn(
    "invoiced_price_per_unit", col("invoiced_price_per_unit").cast(DoubleType())
)

# FIXED: standardize payment_status so "overdue"/"Overdue "/"OVERDUE" all
# match reliably in the risk-classification logic downstream
if "payment_status" in silver_invoices.columns:
    silver_invoices = silver_invoices.withColumn(
        "payment_status", trim(initcap(col("payment_status")))
    )

print(f"[DQ] invoices: raw={raw_count}  after_dedup={dedup_count}  "
      f"duplicates_removed={raw_count - dedup_count}  "
      f"after_null_drop={clean_count}  nulls_dropped={dedup_count - clean_count}")

silver_invoices.show(5)
silver_invoices.printSchema()

# COMMAND ----------

silver_invoices.write.mode("overwrite").saveAsTable("workspace.default.silver_invoices")

# COMMAND ----------

# ============================== VENDORS ==============================
raw_count = bronze_vendors.count()

silver_vendors = bronze_vendors.dropDuplicates(["vendor_id"])
dedup_count = silver_vendors.count()

silver_vendors = silver_vendors.na.drop(subset=["vendor_id", "vendor_name"])
clean_count = silver_vendors.count()

silver_vendors = silver_vendors.withColumn("vendor_name", trim(col("vendor_name")))

# FIXED: blueprint explicitly calls out "convert region to uppercase" —
# this was never done anywhere in the original pipeline
if "region" in silver_vendors.columns:
    silver_vendors = silver_vendors.withColumn("region", trim(upper(col("region"))))

print(f"[DQ] vendors: raw={raw_count}  after_dedup={dedup_count}  "
      f"duplicates_removed={raw_count - dedup_count}  "
      f"after_null_drop={clean_count}  nulls_dropped={dedup_count - clean_count}")

silver_vendors.show(5)
silver_vendors.printSchema()

# COMMAND ----------

silver_vendors.write.mode("overwrite").saveAsTable("workspace.default.silver_vendors")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- sanity check: contract versions per vendor+item (used by SCD2 next)
# MAGIC SELECT vendor_id,
# MAGIC        item_name,
# MAGIC        COUNT(*) AS cnt
# MAGIC FROM workspace.default.silver_contracts
# MAGIC GROUP BY vendor_id, item_name
# MAGIC HAVING COUNT(*) > 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM workspace.default.silver_contracts
# MAGIC WHERE vendor_id='V04827'
# MAGIC AND item_name='E-services'
# MAGIC ORDER BY valid_from;

# COMMAND ----------
