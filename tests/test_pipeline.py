"""
Unit Tests for Data Ingestion and Transformation Pipeline
"""

import sqlite3
from pathlib import Path
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_processed_files_exist():
    csv_file = ROOT_DIR / "data" / "processed" / "orders_transformed.csv"
    parquet_file = ROOT_DIR / "data" / "processed" / "orders_transformed.parquet"
    db_file = ROOT_DIR / "database" / "sales.db"

    assert csv_file.exists(), "orders_transformed.csv missing"
    assert parquet_file.exists(), "orders_transformed.parquet missing"
    assert db_file.exists(), "sales.db missing"


def test_dataset_integrity():
    parquet_file = ROOT_DIR / "data" / "processed" / "orders_transformed.parquet"
    df = pd.read_parquet(parquet_file)

    # Assert exactly 9,994 records
    assert len(df) == 9994, f"Expected 9,994 rows, got {len(df)}"

    # Assert non-null constraints
    assert df["order_id"].isnull().sum() == 0
    assert df["sales"].isnull().sum() == 0
    assert df["profit"].isnull().sum() == 0

    # Assert logical temporal constraints
    assert (df["shipping_days"] >= 0).all(), "Found negative shipping days"

    # Assert discount range
    assert (df["discount"] >= 0.0).all() and (df["discount"] <= 1.0).all()


def test_database_records():
    db_file = ROOT_DIR / "database" / "sales.db"
    conn = sqlite3.connect(db_file)

    cust_count = pd.read_sql("SELECT COUNT(*) AS c FROM customers;", conn)["c"].iloc[0]
    prod_count = pd.read_sql("SELECT COUNT(*) AS c FROM products;", conn)["c"].iloc[0]
    orders_count = pd.read_sql("SELECT COUNT(*) AS c FROM orders;", conn)["c"].iloc[0]

    conn.close()

    assert cust_count == 793, f"Expected 793 customers, got {cust_count}"
    assert prod_count == 1862, f"Expected 1,862 products, got {prod_count}"
    assert orders_count == 9994, f"Expected 9,994 orders, got {orders_count}"


if __name__ == "__main__":
    pytest.main([__file__])
