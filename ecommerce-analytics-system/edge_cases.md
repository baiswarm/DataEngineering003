# Edge Cases Handled

## 1. Empty Result Set
If a SQL query returns no records, the CLI displays:
No data found.

## 2. Invalid Report Name
If an invalid report is entered, the CLI displays:
Invalid Report

## 3. Database Connection Error
The CLI uses try-except to handle database connection failures.

## 4. Missing Values
Missing values were handled during data cleaning using Pandas.

## 5. Duplicate Records
Duplicate records were removed using drop_duplicates().

## 6. Invalid Customer IDs
Orders with invalid customer IDs were removed during data validation.

## 7. Invalid Product IDs
Order items with invalid product IDs were removed during data validation.