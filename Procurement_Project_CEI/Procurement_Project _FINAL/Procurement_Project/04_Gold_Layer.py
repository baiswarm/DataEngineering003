# Databricks notebook source
# FIX LOG (see CHANGELOG_FIXES.md):
#   - One cell was bare `sql\nSELECT * FROM ...` with NO `# MAGIC %sql`
#     prefix. Databricks would run that as plain Python -> `sql` is an
#     undefined name -> NameError. This crashed "Run All" partway
#     through the notebook. Fixed: proper # MAGIC %sql cell.
#   - gold_price_variance_report joined orders/invoices to contracts on
#     vendor_id ONLY (not item_name), and filtered `WHERE c.is_active =
#     true`, which always pulls the CURRENT contract regardless of when
#     the purchase actually happened. That silently defeats the entire
#     point of building SCD2: the "price variance" numbers were being
#     computed against today's price, not the price that was active on
#     each purchase's own date. Fixed: join on vendor_id AND item_name,
#     and match the PO's date inside the matching contract version's
#     [start_date, end_date] window.
#   - gold_vendor_risk_classification used flat dollar thresholds
#     (>1000 / >500) instead of the blueprint's percentage-variance rule,
#     and never looked at payment_status at all, so the "AND/OR has
#     overdue invoices" condition was simply missing. Fixed to match the
#     blueprint's rule exactly.
#   - gold_regional_spend_analysis had no ORDER BY and no ranking, so it
#     didn't actually "show top vendors per region" as required, and
#     skipped the bonus DENSE_RANK() window function entirely. Fixed.

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
# MAGIC SELECT
# MAGIC     o.vendor_id,
# MAGIC     SUM(i.invoiced_price_per_unit * o.quantity_requested) AS total_spend,
# MAGIC     AVG(i.invoiced_price_per_unit) AS avg_invoice_amount,
# MAGIC     COUNT(o.po_id) AS total_orders
# MAGIC FROM workspace.default.silver_orders o
# MAGIC JOIN workspace.default.silver_invoices i
# MAGIC   ON o.po_id = i.po_id
# MAGIC GROUP BY o.vendor_id;

# COMMAND ----------

# FIXED: this cell was plain `sql\nSELECT ...` with no # MAGIC %sql
# prefix, which Databricks runs as Python and crashes on `sql` being an
# undefined name. Now a proper SQL cell.
# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM workspace.default.gold_vendor_spend_summary
# MAGIC LIMIT 10;

# COMMAND ----------

# FIXED: original joined ON o.vendor_id = c.vendor_id only (missing
# item_name -> fans out across every item a vendor sells) and filtered
# `WHERE c.is_active = true` (always the CURRENT contract, not the one
# active when the PO happened). Now joins on vendor_id AND item_name,
# and matches the PO's own date into the contract's [start_date,
# end_date] window, so each purchase is compared against the price that
# was genuinely in force on that date - this is the actual business
# question the blueprint asks the project to answer.
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
# MAGIC         AND o.item_name = c.item_name
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

# FIXED: was flat dollar thresholds (>1000 / >500) with no reference to
# payment_status at all. Now uses percentage variance (variance relative
# to the contract price, not a raw dollar amount that means different
# things for a $10 item vs a $10,000 item) combined with an overdue-
# invoice flag, matching the blueprint's rule exactly:
#   High Risk   = avg % variance > 10 AND has an overdue invoice
#   Medium Risk = avg % variance > 5  OR  has an overdue invoice
#   Low Risk    = everything else
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace.default.gold_vendor_risk_classification AS
# MAGIC WITH pct_variance AS (
# MAGIC     SELECT
# MAGIC         vendor_id,
# MAGIC         AVG(price_difference / negotiated_price) * 100 AS avg_pct_variance
# MAGIC     FROM workspace.default.gold_price_variance_report
# MAGIC     GROUP BY vendor_id
# MAGIC ),
# MAGIC overdue_flags AS (
# MAGIC     SELECT
# MAGIC         vendor_id,
# MAGIC         MAX(CASE WHEN payment_status = 'Overdue' THEN 1 ELSE 0 END) = 1 AS has_overdue
# MAGIC     FROM workspace.default.silver_invoices
# MAGIC     GROUP BY vendor_id
# MAGIC )
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

# FIXED: added ORDER BY plus the bonus DENSE_RANK() window function so
# this table actually "shows top vendors per region" as the blueprint
# asks, instead of an unranked, unordered aggregate.
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace.default.gold_regional_spend_analysis AS
# MAGIC WITH regional AS (
# MAGIC     SELECT
# MAGIC         v.region,
# MAGIC         o.vendor_id,
# MAGIC         SUM(i.invoiced_price_per_unit * o.quantity_requested) AS total_spend
# MAGIC     FROM workspace.default.silver_orders o
# MAGIC     JOIN workspace.default.silver_invoices i
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
# MAGIC -- Top 3 vendors by spend in each region (what "top vendors per
# MAGIC -- region" actually looks like once you have the rank column)
# MAGIC SELECT * FROM workspace.default.gold_regional_spend_analysis
# MAGIC WHERE vendor_rank_in_region <= 3
# MAGIC ORDER BY region, vendor_rank_in_region;

# COMMAND ----------
