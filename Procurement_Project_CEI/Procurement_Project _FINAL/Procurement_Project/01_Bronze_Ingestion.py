

from pyspark.sql.functions import current_timestamp, lit


orders_df = (
    spark.table("workspace.default.orders_1")
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("source_file", lit("orders"))
)

contracts_df = (
    spark.table("workspace.default.contracts_1")
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("source_file", lit("contracts"))
)

invoices_df = (
    spark.table("workspace.default.invoices_1")
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("source_file", lit("invoices"))
)

vendors_df = (
    spark.table("workspace.default.vendors_1")
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("source_file", lit("vendors"))
)

# --- Option B: reading raw CSVs from ADLS Gen2 (uncomment + fill in path) ---
# adls_path = "abfss://<container>@<storage_account>.dfs.core.windows.net/raw"
#
# orders_df = (
#     spark.read.option("header", True).option("inferSchema", True)
#     .csv(f"{adls_path}/purchase_orders.csv")
#     .withColumn("ingestion_timestamp", current_timestamp())
#     .withColumn("source_file", lit("purchase_orders.csv"))
# )
# contracts_df = (
#     spark.read.option("header", True).option("inferSchema", True)
#     .csv(f"{adls_path}/vendor_contracts.csv")
#     .withColumn("ingestion_timestamp", current_timestamp())
#     .withColumn("source_file", lit("vendor_contracts.csv"))
# )
# invoices_df = (
#     spark.read.option("header", True).option("inferSchema", True)
#     .csv(f"{adls_path}/invoices.csv")
#     .withColumn("ingestion_timestamp", current_timestamp())
#     .withColumn("source_file", lit("invoices.csv"))
# )
# vendors_df = (
#     spark.read.option("header", True).option("inferSchema", True)
#     .csv(f"{adls_path}/vendors.csv")
#     .withColumn("ingestion_timestamp", current_timestamp())
#     .withColumn("source_file", lit("vendors.csv"))
# )

# COMMAND ----------

orders_df.show(5)

# COMMAND ----------

contracts_df.show(5)

invoices_df.show(5)

vendors_df.show(5)

# COMMAND ----------

orders_df.printSchema()

# COMMAND ----------

contracts_df.printSchema()

invoices_df.printSchema()

vendors_df.printSchema()

# COMMAND ----------


orders_df.write \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("workspace.default.bronze_orders")

# COMMAND ----------

contracts_df.write \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("workspace.default.bronze_contracts")

# COMMAND ----------

invoices_df.write \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("workspace.default.bronze_invoices")

# COMMAND ----------

vendors_df.write \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("workspace.default.bronze_vendors")

# COMMAND ----------

spark.sql("SELECT * FROM workspace.default.bronze_orders").show(5)

# COMMAND ----------

spark.sql("SELECT * FROM workspace.default.bronze_contracts").show(5)

# COMMAND ----------

spark.sql("SELECT * FROM workspace.default.bronze_invoices").show(5)

# COMMAND ----------

spark.sql("SELECT * FROM workspace.default.bronze_vendors").show(5)

# COMMAND ----------
