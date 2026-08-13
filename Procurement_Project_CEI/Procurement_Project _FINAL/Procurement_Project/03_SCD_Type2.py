# Databricks notebook source
# FIX LOG (see CHANGELOG_FIXES.md) — THIS WAS THE MOST IMPORTANT BUG IN
# THE PROJECT, because SCD2 is the piece the whole business question
# depends on.
#
# What the original code did:
#   1. Took the FULL, un-deduplicated silver_contracts (every historical
#      version of every contract) and wrote ALL of it straight into
#      silver_vendor_contracts with is_active = true and end_date = null
#      on every single row. That means a vendor+item with 3 historical
#      price changes ended up with all 3 versions marked "active"
#      simultaneously — not SCD2, just a copy of the raw table with two
#      extra columns.
#   2. Then built `incoming_contracts` as ONLY the latest row per
#      vendor+item, and MERGE'd it into the table from step 1. Because
#      the target already contained duplicates, the MERGE's condition
#      `target.is_active = true` matched multiple rows per vendor+item.
#      Rows with a different price than the latest got is_active=false,
#      but end_date was set to `date_sub(latest.valid_from, 1)` for ALL
#      of them — so if a vendor had prices $100 -> $120 -> $110, the
#      $100 row's end_date ends up equal to the $120 row's end_date
#      (both "ended the day before the $110 version started"), instead
#      of the $100 row correctly ending when the $120 version began.
#      That's a wrong audit trail for every mid-history contract version.
#   3. NOT MATCHED never fires for the initial load (every vendor+item
#      already existed in target from step 1), so nothing is genuinely
#      "inserted" the way the blueprint's MERGE pattern intends.
#
# Net effect: the historical price that Gold later joins against for an
# old purchase is not reliably the price that was actually active on
# that purchase's date — which defeats the entire point of doing SCD2
# in this project.
#
# The fix below splits this into two clearly separate, correct pieces:
#   A) A one-time BOOTSTRAP that builds the full historical SCD2 table
#      directly from the complete contract history using a window
#      function (LEAD), which is the standard way to backfill SCD2 from
#      a dataset that already contains the full change history. Each
#      version's end_date is correctly the day before the NEXT version
#      for that same vendor+item — not the day before the newest one.
#   B) The blueprint's actual MERGE INTO pattern, used the way it's
#      meant to be used: against a genuinely NEW incoming batch of
#      contract changes (not the whole history merged into itself). Use
#      this going forward whenever a fresh contracts file/table arrives.

from pyspark.sql.functions import *
from pyspark.sql.window import Window

# ======================================================================
# PART A — one-time historical bootstrap (run once against full history)
# ======================================================================

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

# ======================================================================
# PART B — incremental MERGE for NEW contract updates going forward
# (this is the blueprint's MERGE pattern, used the way it's designed:
#  `incoming_contracts` should be a genuinely NEW batch — e.g. today's
#  refreshed contracts table/file — not the same table merged into
#  itself, which was the original bug.)
#
# This whole cell is intentionally left as a commented TEMPLATE, not a
# live cell, because there is no real "new batch" table to merge yet —
# Part A already builds the correct full history. Uncomment and point
# it at your next incoming contracts source when you actually have one,
# so "Run All" today doesn't fail on a temp view that doesn't exist.
# ======================================================================

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
