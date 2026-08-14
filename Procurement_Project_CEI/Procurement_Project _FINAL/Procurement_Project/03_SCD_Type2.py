
from pyspark.sql.functions import *
from pyspark.sql.window import Window



contracts = spark.table("workspace.default.silver_contracts")

vendor_item_window = Window.partitionBy("vendor_id", "item_name").orderBy("valid_from")

bootstrap = (
    contracts
    .withColumn("start_date", col("valid_from"))
    .withColumn("next_valid_from", lead("valid_from").over(vendor_item_window))
    .withColumn(
        "end_date",
        when(col("next_valid_from").isNotNull(), date_sub(col("next_valid_from"), 1))
        .otherwise(lit(None).cast("date"))
    )
    .withColumn("is_active", col("next_valid_from").isNull())
    .drop("next_valid_from", "valid_from")
)

bootstrap.write.mode("overwrite").format("delta") \
    .saveAsTable("workspace.default.silver_vendor_contracts")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Sanity check: exactly one active row per vendor+item, and end_dates
# MAGIC -- form an unbroken chain (each version ends the day the next starts).
# MAGIC -- This query should return ZERO rows. If it returns any, SCD2 is broken.
# MAGIC SELECT vendor_id, item_name, COUNT(*) AS active_rows
# MAGIC FROM workspace.default.silver_vendor_contracts
# MAGIC WHERE is_active = true
# MAGIC GROUP BY vendor_id, item_name
# MAGIC HAVING COUNT(*) <> 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT vendor_id, item_name, negotiated_price, start_date, end_date, is_active
# MAGIC FROM workspace.default.silver_vendor_contracts
# MAGIC ORDER BY vendor_id, item_name, start_date;

# COMMAND ----------



# incoming_contracts_df = spark.table("workspace.default.silver_contracts_new_batch")
# incoming_contracts_df.createOrReplaceTempView("incoming_contracts")
#
# spark.sql("""
#     MERGE INTO workspace.default.silver_vendor_contracts AS target
#     USING incoming_contracts AS source
#     ON target.vendor_id = source.vendor_id
#     AND target.item_name = source.item_name
#     AND target.is_active = true
#     WHEN MATCHED
#       AND (
#         target.negotiated_price <> source.negotiated_price
#         OR COALESCE(target.payment_terms, '') <> COALESCE(source.payment_terms, '')
#       )
#     THEN UPDATE SET
#       target.is_active = false,
#       target.end_date = date_sub(source.valid_from, 1)
#     WHEN NOT MATCHED THEN
#       INSERT (
#         contract_id, vendor_id, item_name, negotiated_price, payment_terms,
#         start_date, end_date, is_active
#       )
#       VALUES (
#         source.contract_id, source.vendor_id, source.item_name,
#         source.negotiated_price, source.payment_terms,
#         source.valid_from, NULL, true
#       )
# """)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM workspace.default.silver_vendor_contracts
# MAGIC WHERE vendor_id='V04827'
# MAGIC AND item_name='E-services'
# MAGIC ORDER BY start_date;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC vendor_id, item_name, negotiated_price, start_date, end_date, is_active
# MAGIC FROM workspace.default.silver_vendor_contracts
# MAGIC ORDER BY vendor_id, item_name, start_date;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM workspace.default.silver_vendor_contracts
# MAGIC WHERE is_active = true;

# COMMAND ----------
