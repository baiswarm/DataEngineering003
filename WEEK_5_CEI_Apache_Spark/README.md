# 🚀 Apache Spark Data Processing using PySpark


This repository contains my **Week 5 Assignment** . The project demonstrates core **Apache Spark (PySpark)** operations for data cleaning, transformation, and aggregation on a retail transaction dataset.

---

## 🎯 Project Objectives

- Perform exploratory data processing using Apache Spark DataFrames.
- Clean and transform raw data using Spark APIs.
- Handle duplicate and missing records.
- Apply filtering, grouping, and aggregation operations.
- Convert raw timestamp values into appropriate Spark data types.
- Build an end-to-end data processing pipeline using PySpark.

---

## 📊 Dataset

The assignment required a dataset containing specific attributes and data quality issues suitable for Spark-based data processing. Since no publicly available dataset fully satisfied these requirements, a **synthetic retail dataset** was generated using an **LLM-assisted workflow** together with **Python data generation libraries (Faker, Pandas, and NumPy)**.

The generated dataset intentionally includes realistic data quality challenges such as:

- Duplicate records
- Missing values
- Inconsistent timestamp formats
- Empty strings
- Invalid field values

These characteristics simulate real-world datasets and provide a practical environment for implementing Spark data cleaning and transformation techniques.

---

## 🛠️ Technologies Used

- Apache Spark (PySpark)
- Python
- Google Colab
- Pandas
- NumPy
- Faker

---

## ⚡ Spark Concepts Demonstrated

- SparkSession
- DataFrame Operations
- Schema Inference (`inferSchema`)
- Duplicate Removal
- Missing Value Handling
- Filtering & Transformations
- GroupBy & Aggregations
- Timestamp Conversion
- End-to-End Data Processing Pipeline

---

## 📚 Assignment Coverage

The notebook includes both theoretical explanations and practical implementations covering:

- MapReduce vs. Apache Spark
- In-Memory Computing
- Spark DataFrame Immutability
- Shuffle Operations
- Handling Null Values
- Schema Inference
- Data Cleaning & Transformation
- Aggregation & Analysis
- End-to-End Spark Processing Pipeline
