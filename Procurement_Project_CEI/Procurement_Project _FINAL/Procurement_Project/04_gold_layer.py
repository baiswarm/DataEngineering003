# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
silver_orders = spark.table("workspace.default.silver_orders")
silver_invoices = spark.table("workspace.default.silver_invoices")
silver_vendor_contracts = spark.table("workspace.default.silver_vendor_contracts")
silver_vendors = spark.table("workspace.default.silver_vendors")

# COMMAND ----------

silver_invoices.printSchema()

# COMMAND ----------

silver_orders.printSchema()

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace.default.gold_vendor_spend_summary AS
# MAGIC WITH invoice_agg AS (
# MAGIC     SELECT po_id, AVG(invoiced_price_per_unit) AS invoiced_price_per_unit
# MAGIC     FROM workspace.default.silver_invoices
# MAGIC     GROUP BY po_id
# MAGIC )
# MAGIC SELECT
# MAGIC     o.vendor_id,
# MAGIC     SUM(i.invoiced_price_per_unit * o.quantity_requested) AS total_spend,
# MAGIC     AVG(i.invoiced_price_per_unit) AS avg_invoice_amount,
# MAGIC     COUNT(o.po_id) AS total_orders
# MAGIC FROM workspace.default.silver_orders o
# MAGIC JOIN invoice_agg i
# MAGIC   ON o.po_id = i.po_id
# MAGIC GROUP BY o.vendor_id;

# COMMAND ----------

# MAGIC
# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM workspace.default.gold_vendor_spend_summary
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace.default.gold_price_variance_report AS
# MAGIC WITH variance_data AS (
# MAGIC     SELECT
# MAGIC         o.vendor_id,
# MAGIC         o.po_id,
# MAGIC         o.item_name,
# MAGIC         o.po_timestamp,
# MAGIC         c.negotiated_price,
# MAGIC         i.invoiced_price_per_unit AS invoice_price,
# MAGIC         i.invoiced_price_per_unit - c.negotiated_price AS price_difference
# MAGIC     FROM workspace.default.silver_orders o
# MAGIC     JOIN workspace.default.silver_invoices i
# MAGIC         ON o.po_id = i.po_id
# MAGIC     JOIN workspace.default.silver_vendor_contracts c
# MAGIC         ON o.vendor_id = c.vendor_id
# MAGIC         AND UPPER(o.item_name) = UPPER(c.item_name)
# MAGIC         AND o.po_timestamp >= c.start_date
# MAGIC         AND (c.end_date IS NULL OR o.po_timestamp <= c.end_date)
# MAGIC )
# MAGIC SELECT
# MAGIC     vendor_id,
# MAGIC     po_id,
# MAGIC     item_name,
# MAGIC     po_timestamp,
# MAGIC     negotiated_price,
# MAGIC     invoice_price,
# MAGIC     price_difference,
# MAGIC     CASE
# MAGIC         WHEN price_difference > 0 THEN 'Overcharged'
# MAGIC         ELSE 'OK'
# MAGIC     END AS charge_status,
# MAGIC     AVG(price_difference) OVER (PARTITION BY vendor_id) AS average_vendor_variance
# MAGIC FROM variance_data;

# COMMAND ----------

# MAGIC
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace.default.gold_vendor_risk_classification AS
# MAGIC WITH pct_variance AS (
# MAGIC     SELECT
# MAGIC         vendor_id,
# MAGIC         AVG(price_difference / NULLIF(negotiated_price, 0)) * 100 AS avg_pct_variance
# MAGIC     FROM workspace.default.gold_price_variance_report
# MAGIC     GROUP BY vendor_id
# MAGIC ),
# MAGIC overdue_flags AS (
# MAGIC     SELECT
# MAGIC         vendor_id,
# MAGIC         FALSE AS has_overdue
# MAGIC     FROM workspace.default.silver_invoices
# MAGIC     GROUP BY vendor_id
# MAGIC )
# MAGIC
# MAGIC SELECT
# MAGIC     v.vendor_id,
# MAGIC     v.avg_pct_variance,
# MAGIC     COALESCE(o.has_overdue, false) AS has_overdue,
# MAGIC     CASE
# MAGIC         WHEN v.avg_pct_variance > 10 AND COALESCE(o.has_overdue, false) THEN 'High Risk'
# MAGIC         WHEN v.avg_pct_variance > 5  OR  COALESCE(o.has_overdue, false) THEN 'Medium Risk'
# MAGIC         ELSE 'Low Risk'
# MAGIC     END AS risk
# MAGIC FROM pct_variance v
# MAGIC LEFT JOIN overdue_flags o
# MAGIC   ON v.vendor_id = o.vendor_id;

# COMMAND ----------

# MAGIC
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace.default.gold_regional_spend_analysis AS
# MAGIC WITH invoice_agg AS (
# MAGIC     SELECT po_id, AVG(invoiced_price_per_unit) AS invoiced_price_per_unit
# MAGIC     FROM workspace.default.silver_invoices
# MAGIC     GROUP BY po_id
# MAGIC ),
# MAGIC regional AS (
# MAGIC     SELECT
# MAGIC         v.region,
# MAGIC         o.vendor_id,
# MAGIC         SUM(i.invoiced_price_per_unit * o.quantity_requested) AS total_spend
# MAGIC     FROM workspace.default.silver_orders o
# MAGIC     JOIN invoice_agg i
# MAGIC         ON o.po_id = i.po_id
# MAGIC     JOIN workspace.default.silver_vendors v
# MAGIC         ON o.vendor_id = v.vendor_id
# MAGIC     GROUP BY v.region, o.vendor_id
# MAGIC )
# MAGIC SELECT
# MAGIC     region,
# MAGIC     vendor_id,
# MAGIC     total_spend,
# MAGIC     DENSE_RANK() OVER (PARTITION BY region ORDER BY total_spend DESC) AS vendor_rank_in_region
# MAGIC FROM regional
# MAGIC ORDER BY region, vendor_rank_in_region;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM workspace.default.gold_vendor_spend_summary;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM workspace.default.gold_price_variance_report;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM workspace.default.gold_vendor_risk_classification;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM workspace.default.gold_regional_spend_analysis;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM workspace.default.gold_regional_spend_analysis
# MAGIC WHERE vendor_rank_in_region <= 3
# MAGIC ORDER BY region, vendor_rank_in_region;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     (SELECT COUNT(*) FROM workspace.default.silver_orders) AS total_orders,
# MAGIC     (SELECT COUNT(DISTINCT po_id) FROM workspace.default.gold_price_variance_report) AS matched_orders,
# MAGIC     ROUND(100.0 * (SELECT COUNT(DISTINCT po_id) FROM workspace.default.gold_price_variance_report)
# MAGIC           / (SELECT COUNT(*) FROM workspace.default.silver_orders), 1) AS match_pct;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS null_po_timestamp_count
# MAGIC FROM workspace.default.silver_orders
# MAGIC WHERE po_timestamp IS NULL;
# MAGIC

# COMMAND ----------

