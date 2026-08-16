# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
from pyspark.sql.functions import *
from pyspark.sql.types import DoubleType, IntegerType

bronze_orders = spark.table("workspace.default.bronze_orders")
bronze_contracts = spark.table("workspace.default.bronze_contracts")
bronze_invoices = spark.table("workspace.default.bronze_invoices")
bronze_vendors = spark.table("workspace.default.bronze_vendors")

# COMMAND ----------


raw_count = bronze_orders.count()

silver_orders = bronze_orders.dropDuplicates(["po_id"])
dedup_count = silver_orders.count()


silver_orders = silver_orders.na.drop(subset=["po_id", "vendor_id", "item_name"])
clean_count = silver_orders.count()

silver_orders = silver_orders.withColumn(
    "po_timestamp",
    when(col("po_timestamp") == "N/A - Unknown Date", None)
    .otherwise(col("po_timestamp"))
)


silver_orders = silver_orders.withColumn("po_timestamp", to_date(col("po_timestamp")))

silver_orders = silver_orders.withColumn("item_name", trim(col("item_name")))


silver_orders = silver_orders.withColumn(
    "quantity_requested", col("quantity_requested").cast(IntegerType())
)

po_timestamp_nulls = silver_orders.filter(col("po_timestamp").isNull()).count()

print(f"[DQ] orders: raw={raw_count}  after_dedup={dedup_count}  "
      f"duplicates_removed={raw_count - dedup_count}  "
      f"after_null_drop={clean_count}  nulls_dropped={dedup_count - clean_count}  "
      f"po_timestamp_nulls={po_timestamp_nulls}")

silver_orders.show(5)
silver_orders.printSchema()

# COMMAND ----------

silver_orders.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("workspace.default.silver_orders")

# COMMAND ----------


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

silver_contracts = silver_contracts.withColumn("valid_from", to_date(col("valid_from")))


silver_contracts = silver_contracts.withColumn(
    "negotiated_price", col("negotiated_price").cast(DoubleType())
)


if "payment_terms" in silver_contracts.columns:
    silver_contracts = silver_contracts.withColumn(
        "payment_terms", trim(upper(col("payment_terms")))
    )

valid_from_nulls = silver_contracts.filter(col("valid_from").isNull()).count()

print(f"[DQ] contracts: raw={raw_count}  after_dedup={dedup_count}  "
      f"duplicates_removed={raw_count - dedup_count}  "
      f"after_null_drop={clean_count}  nulls_dropped={dedup_count - clean_count}  "
      f"valid_from_nulls={valid_from_nulls}")

silver_contracts.show(5)
silver_contracts.printSchema()

# COMMAND ----------

silver_contracts.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("workspace.default.silver_contracts")

# COMMAND ----------


raw_count = bronze_invoices.count()

silver_invoices = bronze_invoices.dropDuplicates(["invoice_id"])
dedup_count = silver_invoices.count()

silver_invoices = silver_invoices.na.drop(subset=["invoice_id", "po_id"])

clean_count = silver_invoices.count()

silver_invoices = silver_invoices.withColumn(
    "invoice_timestamp", expr("try_to_timestamp(invoice_timestamp)")
)

silver_invoices = silver_invoices.withColumn("invoice_timestamp", to_date(col("invoice_timestamp")))


silver_invoices = silver_invoices.withColumn(
    "invoiced_price_per_unit",
    regexp_replace(col("invoiced_price_per_unit"), "[^0-9.]", "").cast(DoubleType())
)



if "payment_status" in silver_invoices.columns:
    silver_invoices = silver_invoices.withColumn(
        "payment_status", trim(initcap(col("payment_status")))
    )

invoice_timestamp_nulls = silver_invoices.filter(col("invoice_timestamp").isNull()).count()

print(f"[DQ] invoices: raw={raw_count}  after_dedup={dedup_count}  "
      f"duplicates_removed={raw_count - dedup_count}  "
      f"after_null_drop={clean_count}  nulls_dropped={dedup_count - clean_count}  "
      f"invoice_timestamp_nulls={invoice_timestamp_nulls}")

silver_invoices.show(5)
silver_invoices.printSchema()

# COMMAND ----------

silver_invoices.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("workspace.default.silver_invoices")

# COMMAND ----------


raw_count = bronze_vendors.count()

silver_vendors = bronze_vendors.dropDuplicates(["vendor_id"])
dedup_count = silver_vendors.count()

silver_vendors = silver_vendors.na.drop(subset=["vendor_id", "vendor_name"])
clean_count = silver_vendors.count()

silver_vendors = silver_vendors.withColumn("vendor_name", trim(col("vendor_name")))


if "region" in silver_vendors.columns:
    silver_vendors = silver_vendors.withColumn("region", trim(upper(col("region"))))

print(f"[DQ] vendors: raw={raw_count}  after_dedup={dedup_count}  "
      f"duplicates_removed={raw_count - dedup_count}  "
      f"after_null_drop={clean_count}  nulls_dropped={dedup_count - clean_count}")

silver_vendors.show(5)
silver_vendors.printSchema()

# COMMAND ----------

silver_vendors.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("workspace.default.silver_vendors")

# COMMAND ----------

# MAGIC %sql
# MAGIC
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

# MAGIC %sql
# MAGIC SELECT COUNT(*) total, SUM(CASE WHEN invoice_id IS NULL THEN 1 ELSE 0 END) null_invoice_id, SUM(CASE WHEN po_id IS NULL THEN 1 ELSE 0 END) null_po_id, SUM(CASE WHEN vendor_id IS NULL THEN 1 ELSE 0 END) null_vendor_id, SUM(CASE WHEN invoiced_price_per_unit IS NULL THEN 1 ELSE 0 END) null_price FROM workspace.default.bronze_invoices;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) FROM workspace.default.silver_invoices;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE workspace.default.bronze_invoices;

# COMMAND ----------

