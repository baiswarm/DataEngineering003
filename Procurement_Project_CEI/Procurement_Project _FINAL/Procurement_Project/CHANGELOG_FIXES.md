# Fix Changelog — Procurement & Vendor Spend Analytics Pipeline

This documents every issue found against the project blueprint and exactly
what changed in each notebook. I don't have access to your Databricks
workspace or your real tables, so I couldn't execute these and grab live
screenshots — the SCD2 and Gold logic was independently validated with a
pandas simulation using synthetic data on the same schema (see
`validate_logic.py` if you want to re-run that proof yourself), and the
numbers came out exactly as expected. You'll still need to run these in
your own workspace against real data before resubmitting/re-presenting.

## 1. Bronze — `01_Bronze_Ingestion.py`

**Bug:** `orders_df` was written with `mode("overwrite")` while
`contracts_df`, `invoices_df`, and `vendors_df` all used `mode("append")`.
The blueprint requires append mode on every Bronze table so re-running the
pipeline adds new records instead of wiping history. Inconsistent write
modes across four near-identical blocks in the same notebook.

**Fix:** All four tables now use `mode("append")`.

**Still open (not a bug, but a real gap):** the blueprint's tech stack
lists ADLS Gen2 + `spark.read.csv()` as the ingestion path. This notebook
reads from pre-loaded workspace tables (`orders_1`, `contracts_1`, etc.)
instead. I left a commented "Option B" block that reads real CSVs from
ADLS Gen2 — swap it in if that's genuinely your source, since your README
and presentation both claim ADLS Gen2 as part of the stack, and the README
currently lists "Integration with Azure Data Lake Storage Gen2" under
*Future Enhancements*, which contradicts the tech stack section.

## 2. Silver — `02_Silver_Cleansing.py`

**Bug 1:** `na.drop()` with no `subset` argument drops a row if *any*
column is null, not just the critical ones the blueprint names
(`vendor_id`, `po_id`, etc.). This can silently delete rows over a null in
some unrelated, non-critical column.
**Fix:** `na.drop(subset=[...])` targeted at the actual key/critical
columns for each table.

**Bug 2:** Price/amount columns (`invoiced_price_per_unit`,
`negotiated_price`) were left as strings in Silver and only cast with
`TRY_CAST` later, repeated three separate times inside the Gold notebook.
The blueprint assigns type casting to the Silver layer.
**Fix:** Explicit `.cast(DoubleType())` / `.cast(IntegerType())` done once
in Silver; Gold no longer needs to cast at all.

**Bug 3:** `region` was never uppercased anywhere, despite the blueprint
explicitly calling this out ("standardize values... convert region to
uppercase"). It lives on `silver_vendors` in your schema (not on the
order, unlike the blueprint's original sample schema).
**Fix:** Added `trim(upper(col("region")))`.

**Bug 4:** Date columns were cast to `to_timestamp()`, not `to_date()`,
so they carried unused time-of-day components. The blueprint asks for
proper `DATE` type.
**Fix:** Switched to `to_date()` on `po_timestamp`, `valid_from`,
`invoice_timestamp`.

**Added:** row-count print statements per table (raw → after dedup → after
null drop), so your Data Quality Summary can cite real numbers instead of
descriptive text with no figures behind it.

## 3. SCD Type 2 — `03_SCD_Type2.py` (the most important fix)

**Bug:** The original notebook wrote the *entire, un-deduplicated*
contract history straight into `silver_vendor_contracts` with
`is_active = true` on every row (so a vendor+item with 3 price changes had
3 simultaneously "active" rows), then MERGE'd a "latest row only" view
into that same table. Because the target already had duplicates, the
`is_active = true` join condition matched multiple target rows per
vendor+item, and every one of them got the *same* `end_date` (the day
before the newest version), instead of each version correctly ending when
the *next* version began. `WHEN NOT MATCHED` never fired for the initial
load either, since every vendor+item already existed in the target.

**Why it matters:** this silently breaks the entire premise of the
project — accurately joining a purchase to the contract that was active
*at the time of that purchase*. See the validation output below: it
directly corrupts the price-variance numbers.

**Fix:** Split into two parts:
- **Part A (bootstrap):** builds the full, correct SCD2 table in one pass
  using `LEAD(valid_from) OVER (PARTITION BY vendor_id, item_name ORDER BY
  valid_from)` to compute each version's `end_date` from the *next*
  version specifically, and `is_active` from whether a next version
  exists. Includes a sanity-check query that should return zero rows
  (more than one active row per vendor+item = broken).
- **Part B (incremental):** the blueprint's `MERGE INTO` pattern, kept
  intact but pointed at a genuinely *new* incoming batch — left as a
  commented template since there's no real "new batch" table yet, so it
  doesn't fail on a missing temp view when you run the notebook today.

### Validation (pandas simulation, not Spark — see `validate_logic.py`)

Synthetic vendor V001 / item "Steel Rod", 3 contract versions:
$100 (Jan) → $120 (Apr) → $110 (Aug, current).

| PO | PO date | Invoice | **Before fix** (always vs. current $110) | **After fix** (vs. contract active on PO date) |
|----|---------|---------|---|---|
| PO1 | Feb 2025 | $105 | −5 → "OK" | **+5 → "Overcharged" (correct)** |
| PO2 | May 2025 | $120 | +10 → "Overcharged" | **$0 → "OK" (correct)** |
| PO3 | Sep 2025 | $108 | −2 → "OK" | −2 → "OK" (unchanged, correctly) |

PO2 is the clearest case: the buggy report flags a $120 invoice as a $10
overcharge because it compares against today's $110 price — but in May,
the contract price genuinely *was* $120, so the invoice was correct. The
buggy logic would have flagged a compliant vendor as overcharging.

## 4. Gold — `04_Gold_Layer.py`

**Bug 1 (breaks the notebook):** one cell was:
```
sql
SELECT * FROM workspace.default.gold_vendor_spend_summary
LIMIT 10;
```
with no `# MAGIC %sql` prefix. Databricks runs that as plain Python,
`sql` is an undefined name → `NameError`, and "Run All" stops there.
**Fix:** proper `# MAGIC %sql` cell.

**Bug 2 (the core business-logic gap):** `gold_price_variance_report`
joined `silver_orders` to `silver_vendor_contracts` on `vendor_id` only
(not `item_name` — this fans out across every item a vendor sells) and
filtered `WHERE c.is_active = true`, which always pulls **today's**
contract regardless of when the purchase happened. This defeats the
purpose of doing SCD2 at all.
**Fix:** join on `vendor_id AND item_name`, and match the PO's own date
into the contract's `[start_date, end_date]` window, so each purchase
compares against the price that was genuinely active on that date.

**Bug 3:** `gold_vendor_risk_classification` used flat dollar thresholds
(`> 1000`, `> 500`) and never referenced `payment_status` at all, so the
blueprint's "AND/OR has overdue invoices" condition was simply missing. A
flat dollar threshold also means different things for a $10 item vs. a
$10,000 item.
**Fix:** percentage variance (`price_difference / negotiated_price`)
combined with an overdue-invoice flag per vendor, matching the blueprint's
rule exactly (>10% AND overdue = High; >5% OR overdue = Medium; else Low).

**Bug 4:** `gold_regional_spend_analysis` had no `ORDER BY` and no
ranking, so it didn't actually "show top vendors per region" as required,
and skipped the bonus `DENSE_RANK()` window function.
**Fix:** added `DENSE_RANK() OVER (PARTITION BY region ORDER BY
total_spend DESC)` plus an example query filtering to the top 3 per
region.

## 5. Deliverables gap (not code — flagging for your submission packet)

- The presentation (`Procurement_Final_Presentation_Updated.pptx`) has
  **zero images** in it. Deliverable #5 in the blueprint explicitly asks
  for a "walkthrough of pipeline with sample output screenshots." Once
  you run the fixed notebooks in your workspace, grab a few `display()` /
  `%sql SELECT *` screenshots of the Gold tables and drop them into the
  deck.
- `Procurement_Data_Quality_Summary.pdf` is descriptive/narrative but
  doesn't cite actual counts. The Silver notebook now prints real
  before/after row counts per table — pull those numbers into the summary
  once you run it.
